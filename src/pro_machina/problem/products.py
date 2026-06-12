from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from itertools import count
from typing import NewType, TypedDict
from warnings import warn

import pro_machina

from ..durations import Duration
from ..exceptions import UnitError
from ..measures import (
    CustomUnit,
    Dimension,
    SizedDimension,
    UnsizedDimension,
    _UnitRegistry,
)
from .constraints import (
    ConstraintLevel,
    HardConstraint,
    SoftConstraint,
)
from .consumables import Consumable


class _ComponentQty(TypedDict):
    item: _Product | Consumable
    qty: Decimal
    unit: str


ProdID = NewType("ProdID", int)


class _Product:
    _ids = count(0)

    def __init__(self, name: str, base_dimension: UnsizedDimension):

        self._id = ProdID(next(self._ids))
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
        self,
        constraints: HardConstraint | list[HardConstraint],
        _level: int = 1,
    ) -> None:

        constraint_level = ConstraintLevel(_level)

        if isinstance(constraints, HardConstraint):
            constraints = [constraints]

        if not all(isinstance(item, HardConstraint) for item in constraints):
            raise TypeError("Constraints must all be of type HardConstraint")

        for constraint in constraints:
            if constraint.product is None:
                constraint._set_product(self)
            constraint._level = constraint_level

        self._hard_constraints.extend(constraints)

    def add_soft_constraint(
        self, constraints: SoftConstraint | list[SoftConstraint]
    ) -> None:
        if isinstance(constraints, SoftConstraint):
            constraints = [constraints]

        if not all(isinstance(item, SoftConstraint) for item in constraints):
            raise TypeError("Constraints must all be of type SoftConstraint")

        to_remove = set()
        for cons in constraints:
            if cons in self._soft_constraints:
                if not pro_machina.options["silence_constraint_overrides"]:
                    warn(
                        "\n"
                        + (
                            f"{constraints.__class__.__name__} has already"
                            f" been defined for {self.name} and is being"
                            f" overwritten by {constraints}\n"
                        ),
                        stacklevel=3,
                    )
                to_remove.add(cons)
            cons._set_product(self)

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


class ContinuousProductGroup:
    """Create a grouping of products that share some characteristic

    This can be useful for situations where products are competing for a
    resource. For example, you might only have a total storage capacity of 50
    pallets that must be shared between multiple different products. Setting
    them in a group ensures that, as an aggregate group, you would not have
    more than 50 pallets, regardless of which individual products are actually
    in storage at any one time.

    Another case might be distinguishing between products that contain gelatine
    and others that do not. Switching from gelatine-based products to
    non-gelatine alternatives can come with a clean-down period of the machine,
    regardless of the individual product from the group being made.

    It's also useful in cases where a particular machine can make multiple
    products at the same rate, for example, so you can adjust them all in one
    go rather than setting the run rate on an individual product level.

    Parameters
    ----------
    name : str
        A name for the grouping
    products : list[_Product] | None, optional
        Optionally instantiate the group with a list of pre-defined
        products. Otherwise, you can instantitate an empty group and add
        products to it as and when they are defined in your code

    Raises
    ------
    TypeError
        Attempted to add something other than a Product to the grouping
    """

    _ids = count(0)

    def __init__(
        self, name: str, products: list[_Product] | None = None
    ) -> None:

        self._id = next(self._ids)
        self.name = name
        self.products: list[_Product] = (
            products if products is not None else []
        )

        if self.products:
            if not all(isinstance(item, _Product) for item in self.products):
                raise TypeError("Incorrect type added to product group")

    def add_products(self, products: _Product | list[_Product]) -> None:
        """Add a product to an existing grouping

        Parameters
        ----------
        products : _Product | list[_Product]
            The product(s) to be added

        Raises
        ------
        TypeError
            Attempted to add something other than a Product to the grouping
        """
        if isinstance(products, _Product):
            self.products.append(products)
        else:
            self.products.extend(products)

        prev_len = len(self.products)
        self.products = list(set(self.products))
        if (
            len(self.products) < prev_len
            and not pro_machina.options["silence_warnings"]
        ):
            warn(
                f"\n Duplicate products were added to group: {self.name}\n",
                stacklevel=3,
            )

        if not all(isinstance(item, _Product) for item in self.products):
            raise TypeError("Incorrect type added to product group")

    def add_component(
        self,
        component: BatchProduct | ContinuousProduct | Consumable,
        qty: SizedDimension | CustomUnit,
        per: SizedDimension,
    ):
        f"""{_Product.add_hard_constraint.__doc__}"""
        for product in self.products:
            product.add_component(component, qty, per)

    def add_hard_constraint(
        self,
        constraints: HardConstraint | list[HardConstraint],
    ) -> None:

        constraint_level = ConstraintLevel(2)

        if isinstance(constraints, HardConstraint):
            constraints = [constraints]

        if not all(isinstance(item, HardConstraint) for item in constraints):
            raise TypeError("Constraints must all be of type HardConstraint")

        for product in self.products:
            for constraint in constraints:
                if constraint.product is None:
                    constraint._set_product(product)

                product.add_hard_constraint(
                    constraint, _level=constraint_level
                )


@dataclass
class ProductBatch:
    name: str
    size: Dimension
    time: Duration


class BatchProduct(_Product):
    def __init__(self, name: str, base_dimension: UnsizedDimension) -> None:
        super().__init__(name, base_dimension)

        self._batches = list[ProductBatch]


__all__ = ["BatchProduct", "ContinuousProduct", "ProductBatch"]
