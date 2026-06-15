from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

import polars as pl

from ...config import Config
from ...util import get_problem_buckets
from ..machines import MachID
from ..products import ProdID
from . import ConstraintLevel, HardConstraint

if TYPE_CHECKING:
    pass


class ConstraintArbiter:
    """A centralised controller of all constraints within a problem

    The Arbiter stores constraints as columns in a dataframe. The rows of the
    dataframe are the time buckets of the problem span, and the columns
    represent the constraint in multiple ways. Each constraint is broken down
    into {constraint.__name__}_{constraint_field}. Each product is given their
    own dataframe stored in a dictionary that details all of the values for
    each constraint listed against that product as
    {constraint.__name__}_level.

    Parameters
    ----------
    problem_start : dt.datetime
        The start datetime of the problem span
    problem_end : dt.datetime
        The end datetime of the problem span
    config : Config
        The problem config specifying the timebucket duration
    """

    def __init__(
        self,
        problem_start: dt.datetime,
        problem_end: dt.datetime,
        config: Config,
    ) -> None:
        self.config = config

        # Params
        self.num_buckets = get_problem_buckets(
            problem_start, problem_end, config.timebucket
        )
        self.start = problem_start
        self.end = problem_end
        self.min_swap_block_size = config.min_default_swap_block
        self.timebucket = config.timebucket

        # When serialising a constraint, these keys represent identifiers of
        # for the application of the constraint. Any other keys that aren't in
        # this list must be field values.
        self.non_field_values = set(
            ["name", "product", "machine", "start_date", "end_date", "_level"]
        )

        # Create a template datetime range for all products
        self.datetime_range = pl.datetime_range(
            self.start,
            self.end,
            interval=dt.timedelta(
                seconds=self.timebucket.to_seconds(),
            ),
            eager=True,
            closed="left",
        )
        assert len(self.datetime_range) == self.num_buckets

        # Containers
        self.product_hard_constraints: dict[ProdID, pl.DataFrame] = {}

    def initialise_product_dataframe(
        self, machines: list[MachID]
    ) -> pl.DataFrame:
        """Create a basic constraint dataframe for a product.

        Currently there are two core constraints that apply across all
        product-machine combinations driven by the minimum and maximum
        production durations to be considered in any single swap. These are
        specified in the Config object.

        These constraints will be entered with the DEFAULT constraint level
        such that they can then be overwritten at a later date.

        Each constraint is stored against a machine in two ways. The format for
        the machine-constraint pairing is as follows:

        `{constraint_name}_{machine_id}_{field}`

        Where `field` is the name of a particular value stored in the
        constraint. A single constraint may have more than one field.
        Additionally, we need to store a `level` property for the constraint to
        indicate how far up in the hierarchy (`ConstraintLevel` Enum) the
        constraint has been set to allow for overwriting. This is stored as:

        `{constraint_name}_{machine_id}_level_{level}`

        Parameters
        ----------
        machines : list[MachID]
            A complete list of all machines that are capable of producing the
            product in question

        Returns
        -------
        pl.DataFrame
            An initialised dataframe for the product.
        """
        # TODO revisit this to make it less brittle if we need to have more
        # defauls in future. For now it works.

        default_constraints = ["MinProductionTime", "MaxProductionTime"]
        default_min_value = self.config.min_default_swap_block.to_seconds()
        default_max_value = self.config.max_default_swap_block.to_seconds()
        default_level = ConstraintLevel.DEFAULT.value

        # Make the "spine" of the df
        df = pl.DataFrame({"datetime": self.datetime_range})
        for con in default_constraints:
            for machine_id in machines:
                if con.startswith("Min"):
                    val = default_min_value
                else:
                    val = default_max_value
                col_name = f"{con}_{machine_id}_value"
                level_field_name = f"{con}_{machine_id}_level"

                df = df.with_columns(
                    pl.lit(val).alias(col_name),
                    pl.lit(default_level).alias(level_field_name),
                )

        return df

    def handle_existing_constraint(
        self,
        df: pl.DataFrame,
        constraint: HardConstraint,
        machines: list[MachID],
    ) -> pl.DataFrame:
        params = constraint._serialise()
        params["start_date"] = (
            params["start_date"]
            if params["start_date"] is not None
            else self.start
        )
        params["end_date"] = (
            params["end_date"] if params["end_date"] is not None else self.end
        )

        con_name = constraint.__class__.__name__
        fields = [
            item for item in params.keys() if item not in self.non_field_values
        ]

        for machine in machines:
            level_col = f"{con_name}_{machine}_level"
            for field in fields:
                named_col = f"{con_name}_{machine}_{field}"
                df = df.with_columns(
                    pl.when(
                        (pl.col(level_col) <= params["_level"])
                        & (pl.col("datetime") >= params["start_date"])
                        & (pl.col("datetime") <= params["end_date"])
                    )
                    .then(params[field])
                    .otherwise(named_col)
                    .alias(named_col),
                    pl.when(
                        (pl.col(level_col) <= params["_level"])
                        & (pl.col("datetime") >= params["start_date"])
                        & (pl.col("datetime") < params["end_date"])
                    )
                    .then(params["_level"])
                    .otherwise(pl.col(level_col))
                    .alias(level_col),
                )
        return df

    def arbitrate_hard_constraints(
        self,
        constraints: list[HardConstraint],
        prod_machine_mapping: dict[ProdID, list[MachID]],
        machine_prod_mapping: dict[MachID, list[ProdID]],
    ) -> None:

        for con in constraints:
            if con.product is not None:
                if con.product._id not in self.product_hard_constraints:
                    df = self.initialise_product_dataframe(
                        prod_machine_mapping[con.product._id]
                    )
                    self.product_hard_constraints[con.product._id] = df
                else:
                    df = self.product_hard_constraints[con.product._id]

                # First need to check whether the constraint has been seen
                # before
                existing_cons = [item.split("_")[0] for item in df.columns]
                already_seen = con.__class__.__name__ in existing_cons

                if already_seen:
                    if con.machine is None:
                        df = self.handle_existing_constraint(
                            df, con, prod_machine_mapping[con.product._id]
                        )
                    else:
                        df = self.handle_existing_constraint(
                            df, con, [con.machine._id]
                        )

                    existing_cons.append(con.__class__.__name__)

            self.product_hard_constraints[con.product._id] = df
