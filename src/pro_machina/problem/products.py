from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from itertools import count
from typing import TypedDict

from ..exceptions import UnitError
from ..measures import (
    CustomUnit,
    Dimension,
    SizedDimension,
    UnitRegistry,
    UnsizedDimension,
)
from .constraints import HardConstraint, SoftConstraint
from .consumables import Consumable


class ConsumableQty(TypedDict):
    item: Consumable
    qty: Decimal


class Product:
    _ids = count(0)

    def __init__(self, name: str, base_dimension: UnsizedDimension):

        self._id: int = next(self._ids)
        self.name: str = name
        self.base_dimension = base_dimension

        self.consumables: list[ConsumableQty] = []
        self._seen_consumables: set[str] = set()

    def add_consumable(
        self,
        consumable: Consumable,
        qty: SizedDimension | CustomUnit,
        per: SizedDimension | None = None,
    ):
        if consumable.name in self._seen_consumables:
            raise UnitError(
                f"{consumable.name} cannot be added twice to {self.name}"
            )

        if isinstance(qty, CustomUnit):
            reg = UnitRegistry()

            # Specifies the SizedDimension of the CustomUnit for this
            # Consumable. e.g. "Bag of Sugar" -> "0.25kg"
            custom_unit = reg.get_measure(qty, consumable)

            # How many of the CustomUnits are we specifying? e.g. 2 Bags
            custom_qty = qty._tmp_qty

            amt = custom_unit._base_qty * custom_qty

        else:
            if not consumable.base_dimension.is_compatible(qty):
                raise UnitError(
                    f"{qty.name()} is an invalid measure for {consumable.name}"
                )
            amt = qty._base_qty

        if per is not None:
            if not self.base_dimension.is_compatible(per):
                raise UnitError(
                    f"{per.name()} is an invalid measure for {self.name}"
                )
            amt /= per._base_qty

        self.consumables.append(ConsumableQty(item=consumable, qty=amt))
        self._seen_consumables.add(consumable.name)

    def add_subproduct(
        self,
        product: Product,
        qty: SizedDimension | CustomUnit,
        per: SizedDimension | None = None,
    ):
        pass


class ContinuousProduct(Product):
    def __init__(self, name: str, base_dimension: UnsizedDimension) -> None:
        super().__init__(name, base_dimension)

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


__all__ = ["BatchProduct", "ContinuousProduct", "ProductBatch"]
