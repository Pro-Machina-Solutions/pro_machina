from dataclasses import dataclass

from ..constraints import AdvancedConstraint
from .hard_constraints import MinProductionTime as MinPT


@dataclass
class MinProductionTime(MinPT, AdvancedConstraint):
    other: int
