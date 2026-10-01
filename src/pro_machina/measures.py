from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from itertools import count
from typing import TYPE_CHECKING, NewType

from ._registries import UnitReg
from .exceptions import UnitError

if TYPE_CHECKING:
    from .problem.consumables import Consumable
    from .problem.products import _Product


UnitID = NewType("UnitID", int)
UnitName = NewType("UnitName", str)


class Dimension:
    qty: Decimal
    symbol: str
    _base_qty: Decimal

    def name(self):
        return type(self).__name__

    def __str__(self) -> str:
        return f"{self.qty} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.qty} {self.symbol}"


class Quantity:
    """Anything that can be turned into a concrete SizedDimension for an item.

    Every public API that accepts a quantity calls ``qty.resolve(item)`` once,
    at the boundary. After that, internals only ever see SizedDimensions.
    """

    def resolve(self, item: _Product | Consumable) -> SizedDimension:
        raise NotImplementedError


class SizedDimension(Quantity):
    name: Callable[[], str]
    is_compatible: Callable[[SizedDimension], bool]
    qty: Decimal
    _base_qty: Decimal
    get_base: Callable[[], Dimension]

    def resolve(self, item: _Product | Consumable) -> SizedDimension:
        if not item.base_dimension.is_compatible(self):
            raise UnitError(
                f"{self.name()} is an invalid measure for {item.name}"
            )
        return self

    # Arithmetic returns a NEW quantity. Mutating in place is dangerous now
    # that sizes are stored and reused (e.g. Bottle's size for an item).
    def __mul__(self, val: float | Decimal | str) -> SizedDimension:
        return type(self)(self.qty * Decimal(val))  # type: ignore[call-arg]

    __rmul__ = __mul__

    def __truediv__(self, val: float | Decimal | str) -> SizedDimension:
        return type(self)(self.qty / Decimal(val))  # type: ignore[call-arg]


############# UNIT #############


class BaseUnit(Dimension):
    """The base, unsized dimension for Unit"""

    @staticmethod
    def is_compatible(other: object) -> bool:
        return isinstance(other, BaseUnit)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Unit:
        return Unit(val)


class Unit(BaseUnit, SizedDimension):
    """Individual items"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal(qty)
        self.symbol = "unit"


############# WEIGHT #############


class Weight(Dimension):
    """The base, unsized dimension for all measures of weight"""

    @staticmethod
    def is_compatible(other: object) -> bool:
        return isinstance(other, Weight)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Gram:
        return Gram(val)


class Gram(Weight, SizedDimension):
    """Metric grams"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal(qty)
        self.symbol = "g"


class Kilo(Weight, SizedDimension):
    """Metric kilograms"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = 1_000 * Decimal(qty)
        self.symbol = "kg"


class Tonne(Weight, SizedDimension):
    """Metric tonnes"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = 1_000_000 * Decimal(qty)
        self.symbol = "tonne"


class Ounce(Weight, SizedDimension):
    """Imperial ounces"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("28.349523") * Decimal(qty)
        self.symbol = "oz"


class Pound(Weight, SizedDimension):
    """Imperial pounds"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("453.59237") * Decimal(qty)
        self.symbol = "lb"


class Ton(Weight, SizedDimension):
    """US (short) tons"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("907_184.74") * Decimal(qty)
        self.symbol = "ton"


############# LENGTH #############


class Length(Dimension):
    """The base, unsized dimension for all measures of length"""

    @staticmethod
    def is_compatible(other: object) -> bool:
        return isinstance(other, Length)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Centimetre:
        return Centimetre(val)


class Centimetre(Length, SizedDimension):
    """Metric centimetres"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal(qty)
        self.symbol = "cm"


class Metre(Length, SizedDimension):
    """Metric metres"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = 100 * Decimal(qty)
        self.symbol = "m"


class Inch(Length, SizedDimension):
    """Imperial inches"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("2.54") * Decimal(qty)
        self.symbol = "in"


class Foot(Length, SizedDimension):
    """Imperial feet"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("30.48") * Decimal(qty)
        self.symbol = "ft"


class Yard(Length, SizedDimension):
    """Imperial yards"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("91.44") * Decimal(qty)
        self.symbol = "yd"


############# AREA #############


class Area(Dimension):
    """The base, unsized dimension for all measures of area"""

    @staticmethod
    def is_compatible(other: object) -> bool:
        return isinstance(other, Area)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Sq_Centimetre:
        return Sq_Centimetre(val)


class Sq_Centimetre(Area, SizedDimension):
    """Metric square centimetres"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal(qty)
        self.symbol = "cm\u00b2"


class Sq_Metre(Area, SizedDimension):
    """Metric square metres"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = 10_000 * Decimal(qty)
        self.symbol = "m\u00b2"


class Sq_Inch(Area, SizedDimension):
    """Imperial square inches"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("6.4516") * Decimal(qty)
        self.symbol = "in\u00b2"


class Sq_Foot(Area, SizedDimension):
    """Imperial square feet"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("929.0304") * Decimal(qty)
        self.symbol = "ft\u00b2"


class Sq_Yard(Area, SizedDimension):
    """Imperial square yards"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("8361.2736") * Decimal(qty)
        self.symbol = "yd\u00b2"


############# VOLUME #############


class Volume(Dimension):
    """The base, unsized dimension for all measures of volume"""

    @staticmethod
    def is_compatible(other: object) -> bool:
        return isinstance(other, Volume)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Cu_Centimetre:
        return Cu_Centimetre(val)


class FluidVolume(Dimension):
    """The base, unsized dimension for all measures of liquid volume"""

    @staticmethod
    def is_compatible(other: object) -> bool:
        return isinstance(other, FluidVolume)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Millilitre:
        return Millilitre(val)


class Cu_Centimetre(Volume, SizedDimension):
    """Metric cubic centimetres"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal(qty)
        self.symbol = "cm\u00b3"


class Cu_Metre(Volume, SizedDimension):
    """Metric cubic metres"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = 1_000_000 * Decimal(qty)
        self.symbol = "m\u00b3"


class Cu_Inch(Volume, SizedDimension):
    """Imperial cubic inches"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("16.387064") * Decimal(qty)
        self.symbol = "in\u00b3"


class Cu_Foot(Volume, SizedDimension):
    """Imperial cubic feet"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("28_316.846592") * Decimal(qty)
        self.symbol = "ft\u00b3"


class Cu_Yard(Volume, SizedDimension):
    """Imperial cubic yards"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("764_554.857984") * Decimal(qty)
        self.symbol = "yd\u00b3"


class Millilitre(FluidVolume, SizedDimension):
    """Metric millilitres"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal(qty)
        self.symbol = "ml"


class Litre(FluidVolume, SizedDimension):
    """Metric litre"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = 1_000 * Decimal(qty)
        self.symbol = "ltr"


class Fl_Ounce(FluidVolume, SizedDimension):
    """Imperial fluid ounces"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("29.57353") * Decimal(qty)
        self.symbol = "fl oz"


class Gallon(FluidVolume, SizedDimension):
    """Imperial gallons"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("3_785.412") * Decimal(qty)
        self.symbol = "gal"


class Barrel(FluidVolume, SizedDimension):
    """US barrels"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal("158_987.3") * Decimal(qty)
        self.symbol = "bbl"


# For type hinting only
UnsizedDimension = (
    type[Area]
    | type[BaseUnit]
    | type[FluidVolume]
    | type[Length]
    | type[Volume]
    | type[Weight]
)


class CustomUnit:
    """A named unit whose size depends on what it contains.

    ```python
    Bottle = CustomUnit("Bottle", FluidVolume)   # optional dimension guard
    Bottle.size_for(straw_flav, Fl_Ounce(12))
    Bottle.size_for(apple_flav, Litre("1.5"))

    Pallet = CustomUnit("Pallet")                # holds anything
    Pallet.size_for(sugar, Tonne("1.5"))
    Pallet.size_for(tub, Unit(400))

    product.add_component(straw_flav, qty=Bottle(2), per=Unit(10_000))
    ```

    Calling the unit, ``Bottle(2)``, gives a ``CustomQty`` - a plain value
    object, exactly like ``Litre(2)`` - which becomes a real SizedDimension as
    soon as it's paired with an item: ``Bottle(2).resolve(straw_flav)`` ->
    ``24 fl oz``.

    Parameters
    ----------
    name : str
        A descriptive name for the unit
    base_dimension : UnsizedDimension | None
        If given, every sizing must be in this dimension (a Bottle is always
        a FluidVolume). Leave as None for containers such as a Pallet, whose
        dimension depends on the item.
    """

    _ids = count(0)

    def __init__(
        self, name: str, base_dimension: UnsizedDimension | None = None
    ) -> None:
        self._id = UnitID(next(self._ids))
        self.name = UnitName(name)
        self.symbol = name
        self.base_dimension = base_dimension
        # Sizes live on the unit itself: item id -> size of ONE of this unit
        self._sizes: dict[int, SizedDimension] = {}
        UnitReg().add(self)

    def size_for(
        self, item: _Product | Consumable, size: SizedDimension
    ) -> None:
        dim = self.base_dimension
        if dim is not None and not dim.is_compatible(size):
            raise UnitError(
                f"{self.name} must be sized as {dim.__name__},"
                f" not {size.name()}"
            )
        self._sizes[item._id] = size.resolve(item)  # checks item compatibility

    def size_of(self, item: _Product | Consumable) -> SizedDimension:
        """The size of ONE of this unit when it holds ``item``."""
        try:
            return self._sizes[item._id]
        except KeyError:
            raise UnitError(
                f"Unit: {self.name} has not been sized for {item.name}"
            ) from None

    def is_sized_for(self, item: _Product | Consumable) -> bool:
        return item._id in self._sizes

    def __call__(self, qty: float | Decimal | str) -> CustomQty:
        return CustomQty(self, qty)

    # No __eq__/__hash__ overrides: identity is exactly what we want.

    def __repr__(self) -> str:
        return f"<CustomUnit: {self.name}>"


class CustomQty(Quantity):
    """``n`` of a CustomUnit, e.g. ``Bottle(2)``. Immutable."""

    def __init__(self, unit: CustomUnit, qty: float | Decimal | str) -> None:
        self.unit = unit
        self.qty = Decimal(qty)

    def name(self) -> str:
        return self.unit.name

    def resolve(self, item: _Product | Consumable) -> SizedDimension:
        # e.g. Bottle(2) for straw_flav -> Fl_Ounce(12) * 2 -> 24 fl oz
        return self.unit.size_of(item) * self.qty

    def __mul__(self, val: float | Decimal | str) -> CustomQty:
        return CustomQty(self.unit, self.qty * Decimal(val))

    __rmul__ = __mul__

    def __truediv__(self, val: float | Decimal | str) -> CustomQty:
        return CustomQty(self.unit, self.qty / Decimal(val))

    def __repr__(self) -> str:
        return f"{self.qty} {self.unit.name}"


__all__ = [
    "Area",
    "Barrel",
    "BaseUnit",
    "Centimetre",
    "Cu_Centimetre",
    "Cu_Foot",
    "Cu_Inch",
    "Cu_Metre",
    "Cu_Yard",
    "CustomQty",
    "CustomUnit",
    "FluidVolume",
    "Fl_Ounce",
    "Foot",
    "Gallon",
    "Gram",
    "Inch",
    "Kilo",
    "Length",
    "Litre",
    "Metre",
    "Millilitre",
    "Ounce",
    "Pound",
    "Quantity",
    "Sq_Centimetre",
    "Sq_Foot",
    "Sq_Inch",
    "Sq_Metre",
    "Sq_Yard",
    "Ton",
    "Tonne",
    "Unit",
    "Volume",
    "Weight",
    "Yard",
]
