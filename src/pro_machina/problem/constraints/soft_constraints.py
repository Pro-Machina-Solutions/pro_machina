from dataclasses import dataclass


class SoftConstraint:
    pass


@dataclass
class OverstockingPenalty(SoftConstraint):
    min_time: int


__all__ = ["SoftConstraint", "OverstockingPenalty"]
