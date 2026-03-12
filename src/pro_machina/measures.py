from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING

from .exceptions import UnitError
from .util import Singleton

if TYPE_CHECKING:
    from .problem.consumables import Consumable
    from .problem.products import _Product


class Dimension:
    qty: Decimal
    symbol: str
    _base_qty: Decimal

    def name(self):
        return self.__class__.__name__


class SizedDimension:
    name: Callable[[], str]
    is_compatible: Callable[[SizedDimension], bool]
    qty: Decimal
    _base_qty: Decimal
    get_base: Callable[[], Dimension]

    def __mul__(self, val: float | Decimal | str) -> SizedDimension:
        val = Decimal(val)
        self.qty *= val
        self._base_qty *= val
        return self

    def __truediv__(self, val: float | Decimal | str) -> SizedDimension:
        val = Decimal(val)
        self.qty /= val
        self._base_qty /= val
        return self


############# UNIT #############


class BaseUnit(Dimension):
    """The base, unsized dimension for Unit"""

    @staticmethod
    def is_compatible(other: SizedDimension) -> bool:
        return isinstance(other, BaseUnit)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Unit:
        return Unit(val)

    def __str__(self) -> str:
        return f"{self.qty} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.qty} {self.symbol}"


class Unit(BaseUnit, SizedDimension):
    """Individual items"""

    def __init__(self, qty: float | Decimal | str) -> None:
        super().__init__()

        self.qty = Decimal(qty)
        self._base_qty = Decimal(qty)
        self.symbol = "unit"

    # def __mul__(self, factor: float | Decimal | str) -> Self:
    #     factor = Decimal(factor)
    #     self.qty * factor
    #     self._base_qty * factor
    #     return self


############# WEIGHT #############


class Weight(Dimension):
    """The base, unsized dimension for all measures of weight"""

    @staticmethod
    def is_compatible(other: SizedDimension) -> bool:
        return isinstance(other, Weight)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Gram:
        return Gram(val)

    def __str__(self) -> str:
        return f"{self.qty} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.qty} {self.symbol}"


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
    """imperial ounces"""

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
    def is_compatible(other: SizedDimension) -> bool:
        return isinstance(other, Length)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Centimetre:
        return Centimetre(val)

    def __str__(self) -> str:
        return f"{self.qty} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.qty} {self.symbol}"


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
    def is_compatible(other: SizedDimension) -> bool:
        return isinstance(other, Area)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Sq_Centimetre:
        return Sq_Centimetre(val)

    def __str__(self) -> str:
        return f"{self.qty} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.qty} {self.symbol}"


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
    def is_compatible(other: SizedDimension) -> bool:
        return isinstance(other, Volume | FluidVolume)

    @staticmethod
    def get_base(val: float | str | Decimal = 1) -> Cu_Centimetre:
        return Cu_Centimetre(val)

    def __str__(self) -> str:
        return f"{self.qty} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.qty} {self.symbol}"


class FluidVolume(Dimension):
    """The base, unsized dimension for all measures of liquid volume"""

    @staticmethod
    def is_compatible(other: SizedDimension) -> bool:
        return isinstance(other, Volume | FluidVolume)

    @staticmethod
    def get_base() -> Millilitre:
        return Millilitre(1)

    def __str__(self) -> str:
        return f"{self.qty} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.qty} {self.symbol}"


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
        self.symbol = "fl oz"


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
    """Create a variable-sized unit for a Product or Consumable

    This is designed to allow for the creation of flexibly-sized units to work
    with. For example, we may want to specify a Pallet unit, which will hold
    different quantities of different products/consumables. That can be done as
    follows:

    ```python
    from pro_machina import Consumable
    from pro_machina.measures import BaseUnit, CustomUnit, Kilo, Tonne, Weight

    consumable_1 = Consumable("Sugar", Weight)
    consumable_2 = Consumable("Flour", Weight)

    Pallet = CustomUnit("A standard pallet", BaseUnit)
    Pallet.size_for(consumable_1, Tonne("1.5"))
    Pallet.size_for(consumable_2, Kilo(1200))
    ```

    Parameters
    ----------
    name : str
        A descriptive name for the unit
    dimension : UnsizedDimension
        The unsized dimension of the unit e.g. Weight or BaseUnit
    """

    def __init__(self, name: str, dimension: UnsizedDimension) -> None:
        self.name = name
        self.dimension = dimension
        self._tmp_qty: Decimal = Decimal(0)

    def size_for(
        self, item: _Product | Consumable, unit: SizedDimension
    ) -> None:
        if not item.base_dimension.is_compatible(unit):
            raise UnitError(
                f"{unit.name()} is an invalid unit measure for {item.name}"
            )
        reg = _UnitRegistry()
        reg.add(self, item, unit)

    def __call__(self, qty: float | Decimal | str):
        tmp = CustomUnit(name=self.name, dimension=self.dimension)
        tmp._tmp_qty = Decimal(qty)
        return tmp

    def __hash__(self):
        return hash(type(self).__name__)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CustomUnit):
            return NotImplemented

        return hash(type(self).__name__) == hash(type(other).__name__)

    def __str__(self):
        return f"<CustomUnit: {self.name}>"

    def __repr__(self):
        return f"<CustomUnit: {self.name}>"


class _UnitRegistry(metaclass=Singleton):
    def __init__(self) -> None:
        self.units: dict[CustomUnit, dict[int, SizedDimension]] = defaultdict(
            dict
        )

    def add(
        self,
        unit: CustomUnit,
        item: _Product | Consumable,
        qty: SizedDimension,
    ) -> None:
        self.units[unit][item._id] = qty

    def get_measure(
        self, unit: CustomUnit, item: _Product | Consumable
    ) -> SizedDimension:
        if self.units.get(unit) is None:
            raise UnitError(f"Unit: {unit.name} has not been registered")

        if self.units[unit].get(item._id) is None:
            raise UnitError(
                f"Unit: {unit.name} has not been sized for {item.name}"
            )
        return self.units[unit][item._id]


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
