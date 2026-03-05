from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .exceptions import UnitError

if TYPE_CHECKING:
    from pro_machina.problem.consumables import Consumable
    from pro_machina.problem.products import Product

import u


class VOLUME(u.QUANTITY):
    pass


Volume = u.Quantity[VOLUME]


_cm3 = u.Unit(Volume, symbol="cm\u00b3", multiplier=1)  # Base unit
_m3 = u.Unit(Volume, symbol="m\u00b3", multiplier=1_000_000)
_ml = u.Unit(Volume, symbol="ml", multiplier=1)
_l = u.Unit(Volume, symbol="litres", multiplier=1_000)


@dataclass
class UNIT:
    """Individual unit"""

    qty: float
    _unit = None

    def _qty(self):
        return self.qty

    def __str__(self):
        return f"{self.qty} unit"


##### WEIGHT #####


@dataclass
class G(u.Quantity):
    """Metric grams"""

    qty: float
    _unit = u.grams(1)

    def _qty(self):
        return u.grams(self.qty)

    def __str__(self):
        return str(self._qty())


@dataclass
class KG(u.Quantity):
    """Metric kilograms"""

    qty: float
    _unit = u.kilograms(1)

    def _qty(self):
        return u.kilograms(self.qty)

    def __str__(self):
        return str(self._qty())


@dataclass
class TONNES(u.Quantity):
    """Metric tonnes"""

    qty: float
    _unit = u.tonnes(1)

    def _qty(self):
        return u.tonnes(self.qty)

    def __str__(self):
        return str(self._qty())


@dataclass
class OZ(u.Quantity):
    """US ounces"""

    qty: float
    _unit = u.grams(1)

    def _qty(self):
        return u.grams(28.349523 * self.qty)

    def __str__(self):
        return f"{self.qty} oz."


@dataclass
class LB(u.Quantity):
    """US pounds"""

    qty: float
    _unit = u.grams(1)

    def _qty(self):
        return u.grams(453.59237 * self.qty)

    def __str__(self):
        return f"{self.qty} lb."


@dataclass
class TONS(u.Quantity):
    """US (short) tons"""

    qty: float
    _unit = u.grams(1)

    def _qty(self):
        return u.grams(907_184.74 * self.qty)

    def __str__(self):
        return f"{self.qty} tons"


##### LENGTH ######


@dataclass
class CM(u.Quantity):
    """Metric centimeters"""

    qty: float
    _unit = u.centimeters(1)

    def _qty(self):
        return u.centimeters(self.qty)

    def __str__(self):
        return f"{self._qty()}"


@dataclass
class M(u.Quantity):
    """Metric meters"""

    qty: float
    _unit = u.meters(1)

    def _qty(self):
        return u.meters(self.qty)

    def __str__(self):
        return f"{self._qty()}"


@dataclass
class IN(u.Quantity):
    """US inch"""

    qty: float
    _unit = u.cm(1)

    def _qty(self):
        return u.centimeters(2.54 * self.qty)

    def __str__(self):
        return f"{self.qty} in."


@dataclass
class FT(u.Quantity):
    """US foot"""

    qty: float
    _unit = u.cm(1)

    def _qty(self):
        return u.centimeters(30.48 * self.qty)

    def __str__(self):
        return f"{self.qty} ft."


##### AREA #####


@dataclass
class SQ_CM(u.Quantity):
    """Metric square centimeters"""

    qty: float
    _unit = u.square_meters(1)

    def _qty(self):
        return u.square_meters(self.qty / 10_000)

    def __str__(self):
        return f"{self.qty}cm\u00b2"


@dataclass
class SQ_M(u.Quantity):
    """Metric square meters"""

    qty: float
    _unit = u.square_meters(1)

    def _qty(self):
        return u.square_meters(self.qty)

    def __str__(self):
        return f"{self._qty()}"


@dataclass
class SQ_IN(u.Quantity):
    """US square inch"""

    qty: float
    _unit = u.square_meters(1)

    def _qty(self):
        return u.square_meters(0.00064516 * self.qty)

    def __str__(self):
        return f"{self.qty} sq in."


@dataclass
class SQ_FT(u.Quantity):
    """US square foot"""

    qty: float
    _unit = u.square_meters(1)

    def _qty(self):
        return u.square_meters(0.09290304 * self.qty)

    def __str__(self):
        return f"{self.qty} sq ft."


##### VOLUME #####


@dataclass
class CU_CM(u.Quantity):
    """Metric cubic centimeters"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _cm3(self.qty)

    def __str__(self):
        return f"{self._qty()}"


@dataclass
class CU_M(u.Quantity):
    """Metric cubic meters"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _m3(self.qty)

    def __str__(self):
        return f"{self._qty()}"


@dataclass
class CU_IN(u.Quantity):
    """US cubic inches"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _cm3(16.3871 * self.qty)

    def __str__(self):
        return f"{self.qty} cu. in."


@dataclass
class CU_FT(u.Quantity):
    """US cubic feet"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _cm3(28_316.84671 * self.qty)

    def __str__(self):
        return f"{self.qty} cu. ft."


@dataclass
class ML(u.Quantity):
    """Metric milliliters"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _ml(self.qty)

    def __str__(self):
        return f"{self._qty()}"


@dataclass
class LTR(u.Quantity):
    """Metric liters"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _l(self.qty)

    def __str__(self):
        return f"{self._qty()}"


@dataclass
class FL_OZ(u.Quantity):
    """US fluid ounce"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _cm3(29.57353 * self.qty)

    def __str__(self):
        return f"{self.qty} fl. oz."


@dataclass
class GAL(u.Quantity):
    """US gallons"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _cm3(3_785.412 * self.qty)

    def __str__(self):
        return f"{self.qty} gal."


@dataclass
class BBL(u.Quantity):
    """US oil barrel"""

    qty: float
    _unit = _cm3(1)

    def _qty(self):
        return _cm3(158_987.3 * self.qty)

    def __str__(self):
        return f"{self.qty} bbl."


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class CustomUnit:
    def __init__(self, name: str, unit: type[u.Quantity]):
        self.name = name
        self._unit: u.Quantity = unit(1)

    def size_for(self, item: Product | Consumable, unit: u.Quantity):
        reg = UnitRegister()
        reg.add(self, item, unit)

    def __call__(self, product: Product, qty: float):
        print(product, qty)

    def __hash__(self):
        return hash(type(self).__name__)

    def __eq__(self, other: CustomUnit):
        return hash(type(self).__name__) == hash(type(other).__name__)

    def __str__(self):
        return "Something"


class UnitRegister(metaclass=_Singleton):
    def __init__(self) -> None:
        self.units: dict[CustomUnit, dict[int, u.Quantity]] = defaultdict(dict)

    def add(
        self, unit: CustomUnit, item: Product | Consumable, qty: u.Quantity
    ) -> None:
        nones = sum([qty._unit is None, unit._unit is None])
        if isinstance(unit._unit, UNIT) and isinstance(qty, UNIT):
            pass
        elif nones == 1:
            raise UnitError("Cannot mix UNIT type with another quantity")
        elif not unit._unit.is_compatible_with(qty._unit):
            raise UnitError(
                f"Custom unit: {unit.name} incompatible with {qty}"
            )


__all__ = [
    BBL,
    CM,
    CU_CM,
    CU_FT,
    CU_IN,
    CU_M,
    CustomUnit,
    FL_OZ,
    FT,
    G,
    GAL,
    IN,
    KG,
    LB,
    LTR,
    M,
    ML,
    OZ,
    SQ_CM,
    SQ_FT,
    SQ_IN,
    SQ_M,
    TONNES,
    TONS,
    UNIT,
    UnitRegister,
]
