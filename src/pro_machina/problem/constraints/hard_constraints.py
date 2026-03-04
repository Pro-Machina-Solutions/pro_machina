from dataclasses import dataclass

from ..constraints import HardConstraint


@dataclass
class MinProductionTime(HardConstraint):
    min_time: int

    def __hash__(self):
        return hash(type(self).__name__)

    def __eq__(self, other: HardConstraint):
        return hash(type(self).__name__) == hash(type(other).__name__)


@dataclass
class MaxProductionTime(HardConstraint):
    max_time: int

    def __hash__(self):
        return hash(type(self).__name__)

    def __eq__(self, other: HardConstraint):
        return hash(type(self).__name__) == hash(type(other).__name__)


__all__ = [MinProductionTime, MaxProductionTime]
