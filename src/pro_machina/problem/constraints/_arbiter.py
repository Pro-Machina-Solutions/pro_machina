from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

import polars as pl

from ...config import Config
from ...util import get_problem_buckets
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
        self.num_buckets = get_problem_buckets(
            problem_start, problem_end, config.timebucket
        )
        self.start = problem_start
        self.end = problem_end
        self.min_swap_block_size = config.min_default_swap_block
        self.timebucket = config.timebucket

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

    def initialise_product_dataframe(self) -> pl.DataFrame:
        return pl.DataFrame(
            {
                "datetime": self.datetime_range,
                "MinProductionTime": (
                    self.config.min_default_swap_block.to_seconds()
                ),
                "MinProductionTime_level": ConstraintLevel.DEFAULT.value,
                "MaxProductionTime": (
                    self.config.max_default_swap_block.to_seconds()
                ),
                "MaxProductionTime_level": ConstraintLevel.DEFAULT.value,
            }
        )

    def arbitrate_hard_constraints(
        self, constraints: list[HardConstraint]
    ) -> None:
        seen_products: set[ProdID] = set()
        for con in constraints:
            if (
                con.product._id is not None
                and con.product._id not in seen_products
            ):
                # Initialise the df for this
                pass
            print(
                type(con).__name__,
                con._level,
                con.machine,
            )
