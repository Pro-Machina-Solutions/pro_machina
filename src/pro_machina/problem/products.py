from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from itertools import count
from typing import TypedDict
from warnings import warn

from ..config import Config
from ..durations import Duration
from ..exceptions import UnitError
from ..measures import (
    CustomUnit,
    Dimension,
    SizedDimension,
    UnsizedDimension,
    _UnitRegistry,
)
from .constraints import HardConstraint, SoftConstraint
from .consumables import Consumable


class _ComponentQty(TypedDict):
    item: _Product | Consumable
    qty: Decimal
    unit: str


class _Product:
    _ids = count(0)

    def __init__(self, name: str, base_dimension: UnsizedDimension):

        self._id: int = next(self._ids)
        self.name = name
        self.base_dimension = base_dimension

        self._consumables: list[_ComponentQty] = []
        self._products: list[_ComponentQty] = []
        self._seen_consumables: set[int] = set()
        self._seen_products: set[int] = set()

        self._hard_constraints: list[HardConstraint] = []
        self._soft_constraints: list[SoftConstraint] = []

        # To avoid recursion, we should just inherit the full product and
        # consumable BOM of anything we add. This should just keep expanding
        # as you go up the chain of parents and we don't necessarily care about
        # separating out and apportioning to child items
        self._bom_products: dict[int, Decimal] = {}
        self._bom_consumables: dict[int, Decimal] = {}

    def add_component(
        self,
        component: BatchProduct | ContinuousProduct | Consumable,
        qty: SizedDimension | CustomUnit,
        per: SizedDimension,
    ):
        """Add either a consumable or a subproduct to the Bill of Materials.

        In each case, the quantity of product must be specified for each
        component being added. So, in the below example, we know that the
        product will be created in FluidVolume measures. However, when adding
        components, we can state their quantity in relation to a variable
        amount to the product being made.

        This is for convenience as not all consumables will be known on a
        per-unit-measure basis but rather on some aggregate basis.

        A simple example of usage:
        ```
        from pro_machina import ContinuousProduct
        from pro_machina.measures import(FluidVolume, Kilo, Litre, Millilitre)

        goop = ContinuousProduct("Goop (TM)", FluidVolume)
        goop.add_component(sugar, qty=Kilo("0.5"), per=Litre(1))
        goop.add_component(starch, qty=Kilo(20), per=Litre(250))
        goop.add_component(rasp_flav, qty=Millilitre(19), per=Litre(2))
        ```

        Parameters
        ----------
        component : BatchProduct | ContinuousProduct | Consumable
            An instance of a pre-defined product or consumable.
        qty : SizedDimension | CustomUnit
            The quantity and dimension of component.
        per : SizedDimension
            The units specified for this product.

        Raises
        ------
        UnitError
            Raised when either trying to add a component more than once or when
            specifying components in units that are not compatible with either
            this product or their own measurement unit.
        """
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
            reg = _UnitRegistry()

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
                _ComponentQty(item=component, qty=amt, unit=unit)
            )
            self._seen_consumables.add(component._id)
            self._bom_consumables[component._id] = (
                self._bom_consumables.get(component._id, 0) + amt
            )
        else:
            self._products.append(
                _ComponentQty(item=component, qty=amt, unit=unit)
            )
            self._seen_products.add(component._id)

            # Hoist up any subproduct BOM data
            self._bom_products[component._id] = amt

            for subprod_id, subprod_qty in component._bom_products.items():
                self._bom_products[subprod_id] = self._bom_products.get(
                    subprod_id, 0
                ) + (amt * subprod_qty)

            for cons_id, cons_qty in component._bom_consumables.items():
                self._bom_consumables[cons_id] = self._bom_consumables.get(
                    cons_id, 0
                ) + (amt * cons_qty)

    def add_hard_constraint(
        self, constraints: HardConstraint | list[HardConstraint]
    ) -> None:
        if isinstance(constraints, HardConstraint):
            constraints = [constraints]

        if not all(isinstance(item, HardConstraint) for item in constraints):
            raise TypeError("Constraints must all be of type HardConstraint")

        conf = Config()
        to_remove = set()
        for cons in constraints:
            if cons in self._hard_constraints:
                if not conf.silence_warnings:
                    warn(
                        (
                            f"{constraints.__class__.__name__} has already"
                            f" been defined for {self.name} and is being"
                            f" overwritten by {constraints}"
                        ).lstrip(),
                        stacklevel=2,
                    )
                to_remove.add(cons)
            cons.set_product(self)

        new_cons = [
            item for item in self._hard_constraints if item not in to_remove
        ]
        new_cons.extend(constraints)
        self._hard_constraints = new_cons

    def add_soft_constraint(
        self, constraints: SoftConstraint | list[SoftConstraint]
    ) -> None:
        if isinstance(constraints, SoftConstraint):
            constraints = [constraints]

        if not all(isinstance(item, SoftConstraint) for item in constraints):
            raise TypeError("Constraints must all be of type SoftConstraint")

        conf = Config()
        to_remove = set()
        for cons in constraints:
            if cons in self._soft_constraints:
                if not conf.silence_warnings:
                    warn(
                        (
                            f"{constraints.__class__.__name__} has already"
                            f" been defined for {self.name} and is being"
                            f" overwritten by {constraints}"
                        ).lstrip(),
                        stacklevel=2,
                    )
                to_remove.add(cons)
            cons.set_product(self)

        new_cons = [
            item for item in self._soft_constraints if item not in to_remove
        ]
        new_cons.extend(constraints)
        self._soft_constraints = new_cons

    def __repr__(self):
        return f"<Product: {self.name}>"


class ContinuousProduct(_Product):
    """Defines a product that can be manufactured for variable periods of time

    Unlike a batch product, these products are produced in a continuous manner
    such that the quantity made is dependent on how long the model chooses to
    run the machine for, rather than a fixed duration and batch quantity.

    Parameters
    ----------
    name : str
        A string identifier for this product
    base_dimension : UnsizedDimension
        The dimension in which this product is sized e.g. FluidVolume or Weight
        etc.
    """

    def __init__(self, name: str, base_dimension: UnsizedDimension) -> None:
        super().__init__(name, base_dimension)


@dataclass
class ProductBatch:
    name: str
    size: Dimension
    time: Duration


class BatchProduct(_Product):
    def __init__(self, name: str, unit_measures) -> None:
        super().__init__(name, unit_measures)

        self._batches = list[ProductBatch]


__all__ = ["BatchProduct", "ContinuousProduct", "ProductBatch"]
