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
            [
                "name",
                "product",
                "machine",
                "start_date",
                "end_date",
            ]
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
        # TODO revisit this to make it less brittle if we need to have more
        # defauls in future. For now it works.

        # The format we want here is {constraint_name}_{machine_id}_{field}
        # for the actual values that apply
        # We also need {constraint_name}_{machine_id}_level_{level}

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
                df = df.with_columns(pl.lit(val).alias(col_name))

                level_field_name = f"{con}_{machine_id}_level"
                df = df.with_columns(
                    pl.lit(default_level).alias(level_field_name)
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

                fields = con._serialise()
                # TODO cherry-picking here for basic testing. Figure out how to
                # handle each case gracefully

                if con.machine is not None:
                    # This means it should apply to every machine that makes
                    # the product
                    machines = prod_machine_mapping[con.product._id]
                    level = fields["level"]
                    con_name = fields["name"]

                    # Now need to check whether this constraint has been seen
                    # before for this product

            print(
                type(con).__name__,
                con._level,
                con.machine,
            )
