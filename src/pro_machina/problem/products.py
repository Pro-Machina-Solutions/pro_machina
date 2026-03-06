from dataclasses import dataclass
from itertools import count
from typing import TypedDict

from ..exceptions import UnitError
from ..measures import Dimension, SizedDimension, UnsizedDimension
from .constraints import HardConstraint, SoftConstraint
from .consumables import Consumable


class ConsumableQty(TypedDict):
    cons: Consumable
    qty: SizedDimension


class Product:
    _ids = count(0)

    def __init__(self, name: str, base_measure: UnsizedDimension):
        self._id: int = next(self._ids)
        self.name: str = name
        self.base_measure = base_measure

        self.consumables = [ConsumableQty]
        self._seen_consumables: set[str] = set()

    def add_consumable(self, consumable: Consumable, qty: SizedDimension):
        if consumable.name in self._seen_consumables:
            raise UnitError(
                f"{consumable.name} cannot be added twice to {self.name}"
            )

        if consumable.base_dimension.is_compatible(qty):
            self.consumables.append(ConsumableQty(cons=consumable, qty=qty))
            self._seen_consumables.add(consumable.name)
        else:
            raise UnitError(
                f"{qty.name()} is an invalid measure for {consumable.name}"
            )


class ContinuousProduct(Product):
    def __init__(self, name: str, base_measure: UnsizedDimension) -> None:
        super().__init__(name, base_measure)

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
    size: Dimension
    time: Dimension


class BatchProduct(Product):
    def __init__(self, name: str, unit_measures) -> None:
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
