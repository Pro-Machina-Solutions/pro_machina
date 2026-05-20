from enum import Enum

from ...util import Singleton
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
    def __init__(self) -> None:
        self.hard_constraints: list[HardConstraint] = []
        self.soft_constraints: list[SoftConstraint] = []

    def add_default_constraints(self, product: _Product) -> None:
        pass

    def add_product_constraint(self, product: _Product) -> None:
        pass
