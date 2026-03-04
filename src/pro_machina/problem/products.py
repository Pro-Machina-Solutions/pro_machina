from dataclasses import dataclass
from itertools import count

import u

from .constraints import HardConstraint, SoftConstraint


class ContinuousProduct:
    _ids = count(0)

    def __init__(
        self,
        name: str,
    ) -> None:
        self._id: int = next(self._ids)
        self.name: str = name

        self._hard_constraints: list[HardConstraint] = []
        self._soft_constraints: list[SoftConstraint] = []

    def add_hard_constraint(
        self, constraint: HardConstraint | list[HardConstraint]
    ) -> None:
        if isinstance(constraint, HardConstraint):
            constraint = [constraint]

        if not all(isinstance(item, HardConstraint) for item in constraint):
            raise TypeError("Constraints must all be of type HardConstraint")

        self._hard_constraints.extend(constraint)

    def add_soft_constraint(
        self, constraint: SoftConstraint | list[SoftConstraint]
    ) -> None:
        if isinstance(constraint, SoftConstraint):
            constraint = [constraint]

        if not all(isinstance(item, SoftConstraint) for item in constraint):
            raise TypeError("Constraints must all be of type SoftConstraint")

        self._soft_constraints.extend(constraint)


@dataclass
class ProductBatch:
    name: str
    size: u.Mass
    time: u.Duration


class BatchProduct:
    _ids = count(0)

    def __init__(
        self,
        name: str,
    ) -> None:
        self._id: int = next(self._ids)
        self.name: str = name

        self._hard_constraints: list[HardConstraint] = []
        self._soft_constraints: list[SoftConstraint] = []
        self._batches = list[ProductBatch]

    def add_hard_constraint(
        self, constraint: HardConstraint | list[HardConstraint]
    ) -> None:
        if isinstance(constraint, HardConstraint):
            constraint = [constraint]

        if not all(isinstance(item, HardConstraint) for item in constraint):
            raise TypeError("Constraints must all be of type HardConstraint")

        self._hard_constraints.extend(constraint)

    def add_soft_constraint(
        self, constraint: SoftConstraint | list[SoftConstraint]
    ) -> None:
        if isinstance(constraint, SoftConstraint):
            constraint = [constraint]

        if not all(isinstance(item, SoftConstraint) for item in constraint):
            raise TypeError("Constraints must all be of type SoftConstraint")

        self._soft_constraints.extend(constraint)


__all__ = [BatchProduct, ContinuousProduct, ProductBatch]
