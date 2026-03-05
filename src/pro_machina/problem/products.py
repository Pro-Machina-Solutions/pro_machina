from dataclasses import dataclass
from itertools import count

import u

from pro_machina.measures import CustomUnit

from ..exceptions import UnitError
from .constraints import HardConstraint, SoftConstraint


class Product:
    _ids = count(0)

    def __init__(
        self, name: str, unit_measures: u.Quantity | list[u.Quantity]
    ):
        self._id: int = next(self._ids)
        self.name: str = name
        if not isinstance(unit_measures, list):
            self.unit_measures = [unit_measures]
        else:
            self.unit_measures = unit_measures

        first_measure = self.unit_measures[0]
        for measure in self.unit_measures:
            if isinstance(measure, CustomUnit):
                continue

            nones = sum([measure._unit is None, first_measure._unit is None])
            if nones == 1:
                raise UnitError(
                    (
                        f"Product: {self.name} cannot be defined as both UNIT"
                        " and some other quantity that is not a CustomUnit."
                    ).lstrip()
                )
            elif nones == 2:
                continue

            elif not first_measure._unit.is_compatible_with(measure._unit):
                raise UnitError(
                    (
                        f"Product measures: {first_measure} and {measure} are"
                        f" incompatible for {self.name}"
                    ).lstrip()
                )


class ContinuousProduct(Product):
    def __init__(
        self, name: str, unit_measures: u.Quantity | list[u.Quantity]
    ) -> None:
        super().__init__(name, unit_measures)

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


class BatchProduct(Product):
    def __init__(
        self, name: str, unit_measures: u.Quantity | list[u.Quantity]
    ) -> None:
        super().__init__(name, unit_measures)

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
