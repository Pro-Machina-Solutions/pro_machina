from __future__ import annotations

import datetime as dt
from enum import Enum

import polars as pl

from ...config import Config
from ...util import Singleton, get_bucket_index, get_problem_buckets
from . import HardConstraint, SoftConstraint


class ConstraintLevel(Enum):
    DEFAULT = 1
    PRODUCT = 2
    PRODUCT_GROUP = 3
    MACHINE = 4
    MACHINE_GROUP = 5
    PROBLEM = 6


class ConstraintArbiter(metaclass=Singleton):
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
        self.hard_constraints: dict[int, pl.DataFrame] = {}
        self.soft_constraints: dict[int, pl.DataFrame] = {}

        # Create a template datetime range for all products
        self.datetime_range = pl.datetime_range(
            self.start,
            self.end,
            interval=dt.timedelta(
                seconds=self.min_swap_block_size.to_seconds(),
            ),
            eager=True,
        )

        assert len(self.datetime_range) == self.num_buckets

    def initialise_product_dataframe(self) -> pl.DataFrame:
        return pl.DataFrame(
            {
                "datetime": self.datetime_range,
                "MinProductionTime": (
                    self.config.min_default_swap_block.to_seconds()
                ),
                "MinProductionTime_level": 1,
                "MaxProductionTime": (
                    self.config.max_default_swap_block.to_seconds()
                ),
                "MaxProductionTime_level": 1,
            }
        )

    def set_hard_constraint(
        self,
        constraints: HardConstraint | list[HardConstraint],
        level: ConstraintLevel,
    ) -> None:
        if isinstance(constraints, HardConstraint):
            constraints = [constraints]

        if not all(isinstance(con, HardConstraint) for con in constraints):
            raise TypeError(
                "Attempted to add something other than a HardConstraint"
            )

        for constraint in constraints:
            cons_start_date = None
            try:
                cons_start_date = constraint.start_date
            except AttributeError:
                pass

            cons_end_date = None
            try:
                cons_end_date = constraint.end_date
            except AttributeError:
                pass

            product_id = constraint.product._id
            cons_name = type(constraint).__name__

            # First check if we know this product, or initialise
            if self.hard_constraints.get(product_id) is None:
                self.hard_constraints[product_id] = (
                    self.initialise_product_dataframe()
                )

            df = self.hard_constraints[product_id]
            # Now look for the constraint name
            if df.get_column(cons_name, default=None) is None:
                df.with_columns(
                    cons_name=pl.when(
                        (pl.col("datetime") >= cons_start_date)
                        & (pl.col("datetime") <= cons_end_date)
                    ).then()
                )

    def set_soft_constraint(
        self,
        constraints: SoftConstraint | list[SoftConstraint],
        level: ConstraintLevel,
    ) -> None:
        if isinstance(constraints, SoftConstraint):
            constraints = [constraints]

        if not all(isinstance(con, SoftConstraint) for con in constraints):
            raise TypeError(
                "Attempted to add something other than a SoftConstraint"
            )

        for constraint in constraints:
            start_index = 0
            try:
                start = constraint.start_date
                assert start is not None
                start_index = get_bucket_index(
                    self._start, self._end, self.config.timebucket, start
                )
            except AttributeError:
                pass

            end_index = self.num_buckets
            try:
                end = constraint.end_date
                assert end is not None
                end_index = get_bucket_index(
                    self._start, self._end, self.config.timebucket, end
                )
            except AttributeError:
                pass
