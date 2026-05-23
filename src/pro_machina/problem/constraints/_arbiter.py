from enum import Enum

import polars as pl

from ...util import Singleton
from ..machines import _Machine
from ..products import _Product
from . import HardConstraint, SoftConstraint


class ConstraintLevel(Enum):
    DEFAULT = 1
    PRODUCT = 2
    PRODUCT_GROUP = 3
    MACHINE = 4
    MACHINE_GROUP = 5
    PROBLEM = 6


class ConstraintArbiter(Singleton):
    """A centralised controller of all constraints within a problem

    The Arbiter stores constraints as columns in a dataframe. The rows of the
    dataframe are the time buckets of the problem span, and the columns
    represent the constraint in multiple ways. Each constraint is broken down
    into {constraint.__name__}_{constraint_field}. Each product is given their
    own dataframe stored in a dictionary that details all of the values for
    each constraint listed against that product as
    {constraint.__name__}_level.
    """

    def __init__(self) -> None:
        self.hard_constraints: dict[int, pl.DataFrame] = {}
        self.soft_constraints: dict[int, pl.DataFrame] = {}

    def set_hard_constraint(
        self,
        product: _Product,
        constraint: HardConstraint | list[HardConstraint],
        level: ConstraintLevel,
        machine: _Machine | None = None,
    ) -> None:
        pass

    def set_soft_constraint(
        self,
        product: _Product,
        constraint: SoftConstraint | list[SoftConstraint],
        level: ConstraintLevel,
        machine: _Machine | None = None,
    ) -> None:
        pass
