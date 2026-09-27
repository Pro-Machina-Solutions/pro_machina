from __future__ import annotations

from itertools import count
from typing import TYPE_CHECKING, NewType

from .costs import Currency
from .util import Singleton

if TYPE_CHECKING:
    from .countries import Country
    from .problem.consumables import ConsID, Consumable


SupplierID = NewType("SupplierID", int)


class _SupplierRegistry(metaclass=Singleton):
    def __init__(self) -> None:
        self._by_name: dict[tuple[str, str], Supplier] = {}
        self._by_id: dict[SupplierID, Supplier] = {}

    def add(self, sup: Supplier) -> None:
        self._by_name[(sup.name, sup.code)] = sup
        self._by_id[sup._id] = sup

    def contains(self, sup: Supplier) -> bool:
        return sup._id in self._by_id

    def get_by_id(self, sup_id: SupplierID) -> Supplier:
        return self._by_id[sup_id]

    def get_by_name(self, name, code) -> Supplier:
        return self._by_name[(name, code)]


class Supplier:
    _ids = count(0)

    def __init__(
        self,
        name: str,
        code: str = "",
        addr_1: str | None = None,
        addr_2: str | None = None,
        addr_3: str | None = None,
        addr_4: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        country: Country | None = None,
        currency: Currency | None = Currency.BASE,
    ) -> None:
        self._id = SupplierID(next(self._ids))
        self.name = name
        self.code = code
        self.addr_1 = addr_1
        self.addr_2 = addr_2
        self.addr_3 = addr_3
        self.addr_4 = addr_4
        self.phone = phone
        self.website = website
        self.country = country
        self.currency = currency

        self.consumbles: dict[ConsID, Consumable] = {}

    def __hash__(self) -> int:
        return hash(f"{str(self._id)}_{self.code}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Supplier):
            return NotImplemented
        return hash(self) == hash(other)
