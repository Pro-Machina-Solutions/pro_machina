from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .problem.consumables import Consumable
    from .problem.products import Product


class Dimension:
    def name(self):
        return self.__class__.__name__


class SizedDimension:
    pass


############# UNIT #############


class BaseUnit(Dimension):
    @staticmethod
    def is_compatible(other) -> bool:
        return isinstance(other, BaseUnit)

    def __str__(self) -> str:
        return f"{self.raw_value} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.raw_value} {self.symbol}"


class Unit(BaseUnit):
    """Individual items"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal(value)
        self.symbol = "unit"


############# WEIGHT #############


class Weight(Dimension):
    @staticmethod
    def is_compatible(other):
        return isinstance(other, Weight)

    def __str__(self) -> str:
        return f"{self.raw_value} {self.symbol}"

    def __repr__(self) -> str:
        return f"{self.raw_value} {self.symbol}"


class Gram(Weight, SizedDimension):
    """Metric grams"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal(value)
        self.symbol = "g"


class Kilo(Weight):
    """Metric kilograms"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = 1_000 * Decimal(value)
        self.symbol = "kg"


class Tonne(Weight):
    """Metric tonnes"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = value
        self._base_value = 1_000_000 * Decimal(value)
        self.symbol = "tonne"


class Ounce(Weight):
    """imperial ounces"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("28.349523") * Decimal(value)
        self.symbol = "oz"


class Pound(Weight):
    """Imperial pounds"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("453.59237") * Decimal(value)
        self.symbol = "lb"


class Ton(Weight):
    """US (short) tons"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("907_184.74") * Decimal(value)
        self.symbol = "ton"


############# LENGTH #############


class Length(Dimension):
    def is_compatible(self, other) -> bool:
        return isinstance(other, type(self))

    def __str__(self) -> str:
        return f"{self.raw_value} {self.symbol}"


class Centimetre(Length):
    """Metric centimetres"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal(value)
        self.symbol = "cm"


class Metre(Length):
    """Metric metres"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = 100 * Decimal(value)
        self.symbol = "m"


class Inch(Length):
    """Imperial inches"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("2.54") * Decimal(value)
        self.symbol = "in"


class Foot(Length):
    """Imperial feet"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("30.48") * Decimal(value)
        self.symbol = "ft"


class Yards(Length):
    """Imperial yards"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("91.44") * Decimal(value)
        self.symbol = "yd"


############# AREA #############


class Area(Dimension):
    def is_compatible(self, other) -> bool:
        return isinstance(other, type(self))

    def __str__(self) -> str:
        return f"{self.raw_value} {self.symbol}"


class Sq_Centimetre(Area):
    """Metric square centimetres"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal(value)
        self.symbol = "cm\u00b2"


class Sq_Metre(Area):
    """Metric square metres"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = 10_000 * Decimal(value)
        self.symbol = "m\u00b2"


class Sq_Inch(Area):
    """Imperial square inches"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("6.4516") * Decimal(value)
        self.symbol = "in\u00b2"


class Sq_Foot(Area):
    """Imperial square feet"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("929.0304") * Decimal(value)
        self.symbol = "ft\u00b2"


class Sq_Yard(Area):
    """Imperial square yards"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("8361.2736") * Decimal(value)
        self.symbol = "yd\u00b2"


############# VOLUME #############


class Volume(Dimension):
    def is_compatible(self, other) -> bool:
        return isinstance(other, type(self))

    def __str__(self) -> str:
        return f"{self.raw_value} {self.symbol}"


class Cu_Centimetre(Area):
    """Metric cubic centimetres"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal(value)
        self.symbol = "cm\u00b3"


class Cu_Metre(Area):
    """Metric cubic metres"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = 1_000_000 * Decimal(value)
        self.symbol = "m\u00b3"


class Millilitre(Volume):
    """Metric millilitres"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal(value)
        self.symbol = "ml"


class Litre(Volume):
    """Metric litre"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = 1_000 * Decimal(value)
        self.symbol = "ltr"


class FL_Ounce(Area):
    """Imperial fluid ounces"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("29.57353") * Decimal(value)
        self.symbol = "fl oz"


class Gallon(Area):
    """Imperial gallons"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("3_785.412") * Decimal(value)
        self.symbol = "fl oz"


class Barrel(Area):
    """US barrels"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("158_987.3") * Decimal(value)
        self.symbol = "bbl"


class Cu_Inch(Area):
    """Imperial cubic inches"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("16.387064") * Decimal(value)
        self.symbol = "in\u00b3"


class Cu_Foot(Area):
    """Imperial cubic feet"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("28_316.846592") * Decimal(value)
        self.symbol = "ft\u00b3"


class Cu_Yard(Area):
    """Imperial cubic yards"""

    def __init__(self, value: float | Decimal | str) -> None:
        super().__init__()

        self.raw_value = Decimal(value)
        self._base_value = Decimal("764_554.857984") * Decimal(value)
        self.symbol = "yd\u00b3"


class CustomUnit:
    def __init__(self, name: str, dimension: UnsizedDimension):
        self.name = name
        self.dimension = dimension

    def size_for(self, item: Product | Consumable, unit: SizedDimension):
        reg = UnitRegister()
        reg.add(self, item, unit)

    def __call__(
        self, product: Product | Consumable, qty: float | Decimal | str
    ) -> None:
        print()

    def __hash__(self):
        return hash(type(self).__name__)

    def __eq__(self, other: CustomUnit):
        return hash(type(self).__name__) == hash(type(other).__name__)

    def __str__(self):
        return f"<CustomUnit: {self.name}>"

    def __repr__(self):
        return f"<CustomUnit: {self.name}>"


UnsizedDimension = Area | BaseUnit | Length | Volume | Weight


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class UnitRegister(metaclass=_Singleton):
    def __init__(self) -> None:
        self.units: dict[CustomUnit, dict[int, SizedDimension]] = defaultdict(
            dict
        )

    def add(self, unit: CustomUnit, item: Product | Consumable, qty) -> None:
        self.units[unit][item._id] = qty

        print(self.units)


__all__ = [
    Area,
    Barrel,
    BaseUnit,
    Centimetre,
    Cu_Centimetre,
    Cu_Foot,
    Cu_Inch,
    Cu_Metre,
    Cu_Yard,
    CustomUnit,
    FL_Ounce,
    Foot,
    Gallon,
    Gram,
    Inch,
    Kilo,
    Length,
    Litre,
    Metre,
    Millilitre,
    Ounce,
    Pound,
    Sq_Centimetre,
    Sq_Foot,
    Sq_Inch,
    Sq_Metre,
    Sq_Yard,
    Ton,
    Tonne,
    Unit,
    Volume,
    Weight,
    Yards,
]
