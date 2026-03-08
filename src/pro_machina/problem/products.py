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


class ComponentQty(TypedDict):
    item: Product | Consumable
    qty: Decimal
    unit: str


class Product:
    _ids = count(0)

    def __init__(self, name: str, base_dimension: UnsizedDimension):

        self._id: int = next(self._ids)
        self.name = name
        self.base_dimension = base_dimension

        self._consumables: list[ComponentQty] = []
        self._products: list[ComponentQty] = []
        self._seen_consumables: set[int] = set()
        self._seen_products: set[int] = set()

    def add_component(
        self,
        component: Product | Consumable,
        qty: SizedDimension | CustomUnit,
        per: SizedDimension,
    ):
        if (
            component._id in self._seen_consumables
            or component._id in self._seen_products
        ):
            raise UnitError(
                f"{component.name} cannot be added twice to {self.name}"
            )

        if not self.base_dimension.is_compatible(per):
            raise UnitError(
                f"{per.name()} is an invalid measure for {self.name}"
            )

        if isinstance(qty, CustomUnit):
            reg = UnitRegistry()

            # Specifies the SizedDimension of the CustomUnit for this
            # Consumable. e.g. "Bag of Sugar" -> "0.25kg"
            custom_unit = reg.get_measure(qty, component)

            # How many of the CustomUnits are we specifying? e.g. 2 Bags
            custom_qty = qty._tmp_qty

            base_dimension = self.base_dimension.get_base()
            amt = (custom_unit._base_qty * custom_qty) / base_dimension.qty

            unit = custom_unit.get_base().symbol

        else:
            if not component.base_dimension.is_compatible(qty):
                raise UnitError(
                    f"{qty.name()} is an invalid measure for {component.name}"
                )
            amt = qty._base_qty
            unit = qty.get_base().symbol

        amt /= per._base_qty

        if isinstance(component, Consumable):
            self._consumables.append(
                ComponentQty(item=component, qty=amt, unit=unit)
            )
            self._seen_consumables.add(component._id)
        else:
            self._products.append(
                ComponentQty(item=component, qty=amt, unit=unit)
            )
            self._seen_products.add(component._id)

    def __repr__(self):
        return f"<Product: {self.name}>"


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
