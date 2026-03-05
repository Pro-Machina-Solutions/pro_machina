from collections import defaultdict
from dataclasses import dataclass

import u

from .problem.consumables import Consumable
from .problem.products import Product


class VOLUME(u.QUANTITY):
    pass


Volume = u.Quantity[VOLUME]

_cm3 = u.Unit(Volume, symbol="cm\u00b3", multiplier=1)  # Base unit
_m3 = u.Unit(Volume, symbol="m\u00b3", multiplier=1_000_000)
_ml = u.Unit(Volume, symbol="ml", multiplier=1)
_l = u.Unit(Volume, symbol="litres", multiplier=1_000)


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class UnitRegister(metaclass=_Singleton):
    def __init__(self) -> None:
        self.prod_units: dict[str, dict[int, u.Quantity]] = defaultdict(dict)
        self.cons_units: dict[str, dict[int, u.Quantity]] = defaultdict(dict)

    def add(
        self, name: str, item: Product | Consumable, qty: u.Quantity
    ) -> None:
        if isinstance(item, Product):
            self.prod_units[name][item._id] = qty
        else:
            self.cons_units[name][item._id] = qty


@dataclass
class UNIT(u.Quantity):
    """Individual unit"""

    qty: float

    def _qty(self):
        return self.qty

    def __repr__(self):
        return f"{self.qty} unit"


##### WEIGHT #####


@dataclass
class G(u.QUANTITY):
    """Metric grams"""

    qty: float

    def _qty(self):
        return u.grams(self.qty)

    def __repr__(self):
        return str(self._qty())


@dataclass
class KG(u.QUANTITY):
    """Metric kilograms"""

    qty: float

    def _qty(self):
        return u.kilograms(self.qty)

    def __repr__(self):
        return str(self._qty())


@dataclass
class TONNES(u.QUANTITY):
    """Metric tonnes"""

    qty: float

    def _qty(self):
        return u.tonnes(self.qty)

    def __repr__(self):
        return str(self._qty())


@dataclass
class OZ(u.QUANTITY):
    """US ounces"""

    qty: float

    def _qty(self):
        return u.grams(28.349523 * self.qty)

    def __repr__(self):
        return f"{self.qty} oz."


@dataclass
class LB(u.QUANTITY):
    """US pounds"""

    qty: float

    def _qty(self):
        return u.grams(453.59237 * self.qty)

    def __repr__(self):
        return f"{self.qty} lb."


@dataclass
class TONS(u.QUANTITY):
    """US (short) tons"""

    qty: float

    def _qty(self):
        return u.grams(907_184.74 * self.qty)

    def __repr__(self):
        return f"{self.qty} tons"


##### LENGTH ######


@dataclass
class CM(u.QUANTITY):
    """Metric centimeters"""

    qty: float

    def _qty(self):
        return u.centimeters(self.qty)

    def __repr__(self):
        return f"{self._qty()}"


@dataclass
class M(u.QUANTITY):
    """Metric meters"""

    qty: float

    def _qty(self):
        return u.meters(self.qty)

    def __repr__(self):
        return f"{self._qty()}"


@dataclass
class IN(u.QUANTITY):
    """US inch"""

    qty: float

    def _qty(self):
        return u.centimeters(2.54 * self.qty)

    def __repr__(self):
        return f"{self.qty} in."


@dataclass
class FT(u.QUANTITY):
    """US foot"""

    qty: float

    def _qty(self):
        return u.centimeters(30.48 * self.qty)

    def __repr__(self):
        return f"{self.qty} ft."


##### AREA #####


@dataclass
class SQ_CM(u.QUANTITY):
    """Metric square centimeters"""

    qty: float

    def _qty(self):
        return u.square_meters(self.qty / 10_000)

    def __repr__(self):
        return f"{self.qty}cm\u00b2"


@dataclass
class SQ_M(u.QUANTITY):
    """Metric square meters"""

    qty: float

    def _qty(self):
        return u.square_meters(self.qty)

    def __repr__(self):
        return f"{self._qty()}"


@dataclass
class SQ_IN(u.QUANTITY):
    """US square inch"""

    qty: float

    def _qty(self):
        return u.square_meters(0.00064516 * self.qty)

    def __repr__(self):
        return f"{self.qty} sq in."


@dataclass
class SQ_FT(u.QUANTITY):
    """US square foot"""

    qty: float

    def _qty(self):
        return u.square_meters(0.09290304 * self.qty)

    def __repr__(self):
        return f"{self.qty} sq ft."


##### VOLUME #####


@dataclass
class CU_CM(u.QUANTITY):
    """Metric cubic centimeters"""

    qty: float

    def _qty(self):
        return _cm3(self.qty)

    def __repr__(self):
        return f"{self._qty()}"


@dataclass
class CU_M(u.QUANTITY):
    """Metric cubic meters"""

    qty: float

    def _qty(self):
        return _m3(self.qty)

    def __repr__(self):
        return f"{self._qty()}"


@dataclass
class CU_IN(u.QUANTITY):
    """US cubic inches"""

    qty: float

    def _qty(self):
        return _cm3(16.3871 * self.qty)

    def __repr__(self):
        return f"{self.qty} cu. in."


@dataclass
class CU_FT(u.QUANTITY):
    """US cubic feet"""

    qty: float

    def _qty(self):
        return _cm3(28_316.84671 * self.qty)

    def __repr__(self):
        return f"{self.qty} cu. ft."


@dataclass
class ML(u.QUANTITY):
    """Metric milliliters"""

    qty: float

    def _qty(self):
        return _ml(self.qty)

    def __repr__(self):
        return f"{self._qty()}"


@dataclass
class LTR(u.QUANTITY):
    """Metric liters"""

    qty: float

    def _qty(self):
        return _l(self.qty)

    def __repr__(self):
        return f"{self._qty()}"


@dataclass
class FL_OZ(u.QUANTITY):
    """US fluid ounce"""

    qty: float

    def _qty(self):
        return _cm3(29.57353 * self.qty)

    def __repr__(self):
        return f"{self.qty} fl. oz."


@dataclass
class GAL(u.QUANTITY):
    """US gallons"""

    qty: float

    def _qty(self):
        return _cm3(3_785.412 * self.qty)

    def __repr__(self):
        return f"{self.qty} gal."


@dataclass
class BBL(u.QUANTITY):
    """US oil barrel"""

    qty: float

    def _qty(self):
        return _cm3(158_987.3 * self.qty)

    def __repr__(self):
        return f"{self.qty} bbl."


__all__ = [
    BBL,
    CM,
    CU_CM,
    CU_FT,
    CU_IN,
    CU_M,
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
