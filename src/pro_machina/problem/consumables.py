from __future__ import annotations

from itertools import count
from typing import Any, NewType

# if TYPE_CHECKING:
from ..costs import PriceBand, PurchaseCost
from ..measures import UnsizedDimension
from ..suppliers import SupplierID
from ..util import Singleton

ConsID = NewType("ConsID", int)


class _ConsumableRegistry(metaclass=Singleton):
    def __init__(self) -> None:
        self._by_name: dict[tuple[str, str], Consumable] = {}
        self._by_id: dict[ConsID, Consumable] = {}

    def add(self, cons: Consumable) -> None:
        self._by_name[(cons.name, cons.code)] = cons
        self._by_id[cons._id] = cons

    def contains(self, cons: Consumable) -> bool:
        return cons._id in self._by_id

    def get_by_id(self, cons_id: ConsID) -> Consumable:
        return self._by_id[cons_id]


class Consumable:
    """Represents some item that is not manufactured on site.

    Consumables are, by default, rate-limiting. This means that if there is no
    available stock, any products that depend on this item will not be made.
    However, this can be quite tedius to specify for every consumable,
    especially for high-use, high-availability consumables where supply can be
    assumed to be always available.

    If rate_limiting is set to False, the use of consumables will still be
    tracked so that you can calculate the expected demand over the solver
    period but it will be assumed that there is infinite supply.

    Parameters
    ----------
    name : str
        A representative name for the consumable.
    base_dimension : UnsizedDimension
        The dimension in which this product is sized e.g. FluidVolume or Weight
        etc.
    code : str
        An optional additional string to differentiate consumables with the
        same name but distinct properties. By default, an empty string.
    meta : dict[Any, Any] | None
            An optional dictionary of custom properties to store against this
            consumable item. By default, None.
    rate_limiting : bool
        Whether the stock level of this consumable should be taken into account
        when trying to create products. By default, True.
    purchase_cost : PurchaseCost | list[PurchaseCost | None
        Define the purchase cost of the unit across multiple order sizes. If
        left None (the default) then zero cost will be assumed.
    """

    _ids = count(1_000_000)

    def __init__(
        self,
        name: str,
        base_dimension: UnsizedDimension,
        code: str = "",
        meta: dict[Any, Any] | None = None,
        rate_limiting: bool = True,
        purchase_costs: PurchaseCost | list[PurchaseCost] | None = None,
    ) -> None:
        self._id = ConsID(next(self._ids))
        self.name = name
        self.code = code
        self.base_dimension = base_dimension
        self.rate_limiting = rate_limiting
        self.meta = meta if meta is not None else {}

        reg = _ConsumableRegistry()
        reg.add(self)

        self.purchase_costs: list[PriceBand] = []
        self.suppliers: set[SupplierID] = set()

        if purchase_costs is not None:
            self._register_price_bands(purchase_costs)

    def _register_price_bands(
        self, purchase_costs: PurchaseCost | list[PurchaseCost]
    ) -> None:

        if isinstance(purchase_costs, PurchaseCost):
            purchase_costs = [purchase_costs]

        for p in purchase_costs:
            if not isinstance(p, PurchaseCost):
                raise TypeError("Invalid PurchaseCost instance.")
            p._check_unit_compatibility(self)

            for price_band in p.price_bands:
                self.purchase_costs.append(price_band)
                if p.supplier is not None:
                    self.suppliers.add(p.supplier._id)

    def __repr__(self) -> str:
        return f"<Consumable: {self.name}>"

    def __hash__(self) -> int:
        return hash(f"{str(self._id)}_{self.code}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Consumable):
            return NotImplemented
        return hash(self) == hash(other)

    @staticmethod
    def get_all() -> list[Consumable]:
        """Return all consumables defined so far

        Returns
        -------
        list[Consumable]
            All consumables defined so far
        """
        reg = _ConsumableRegistry()
        return list(reg._by_id.values())


__all__ = ["Consumable"]
