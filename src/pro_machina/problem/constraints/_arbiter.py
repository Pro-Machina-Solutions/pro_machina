from ...util import Singleton
from . import HardConstraint, SoftConstraint


class ConstraintArbiter(Singleton):
    def __init__(self) -> None:
        self.product_hard_constraints: list[HardConstraint] = []
        self.machine_hard_constraints: list[HardConstraint] = []
        self.prodblem_hard_constraints: list[HardConstraint] = []

        self.product_soft_constraints: list[SoftConstraint] = []
        self.machine_soft_constraints: list[SoftConstraint] = []
        self.prodblem_soft_constraints: list[SoftConstraint] = []
