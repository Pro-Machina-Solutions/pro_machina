from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .costs import Currency
    from .countries import Country


class Supplier:
    def __init__(
        self,
        name: str,
        supplier_code: str | None = None,
        addr_1: str | None = None,
        addr_2: str | None = None,
        addr_3: str | None = None,
        addr_4: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        country: Country | None = None,
        currency: Currency | None = None,
    ):
        self.name = name
        self.supplier_code = supplier_code
        addr_1 = addr_1
        addr_2 = addr_2
        addr_3 = addr_3
        addr_4 = addr_4
        phone = phone
        website = website
        country = country
        currency = currency
