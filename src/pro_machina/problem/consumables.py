from __future__ import annotations

from itertools import count
from typing import Any, TypedDict

from ..measures import UnsizedDimension
from ..util import Singleton


class _MetaConsumable(TypedDict):
    _id: int
    name: str
    base_dimension: UnsizedDimension
    rate_limiting: bool
    meta: dict[Any, Any]


class _ConsumableRegistry(metaclass=Singleton):
    def __init__(self) -> None:
        self._by_name: dict[str, _MetaConsumable] = {}
        self._by_id: dict[int, _MetaConsumable] = {}

    def add(self, cons: _MetaConsumable) -> None:
        self._by_name[cons["name"]] = cons
        self._by_id[cons["_id"]] = cons


class Consumable:
    """Represents some item that is not manufactured on site

    Consumables are by default rate-limiting. This means that if there is no
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
        A representative name for the consumable
    base_dimension : UnsizedDimension
        The dimension in which this product is sized e.g. FluidVolume or Weight
        etc.
    rate_limiting : bool
        Whether the stock level of this consumable should be taken into account
        when trying to create products. By default, True.
    """

    _ids = count(1_000_000)

    def __init__(
        self,
        name: str,
        base_dimension: UnsizedDimension,
        meta: dict[Any, Any] | None = None,
        rate_limiting: bool = True,
        _id: int | None = None,
    ) -> None:
        if _id is None:
            self._id = next(self._ids)
        else:
            self._id = _id
        self.name: str = name
        self.base_dimension = base_dimension
        self.rate_limiting = rate_limiting
        self.meta = meta if meta is not None else {}

        reg = _ConsumableRegistry()
        reg.add(
            _MetaConsumable(
                name=name,
                base_dimension=base_dimension,
                rate_limiting=rate_limiting,
                _id=self._id,
                meta=self.meta,
            )
        )

    @staticmethod
    def get_all() -> list[Consumable]:
        reg = _ConsumableRegistry()
        return [
            Consumable(
                name=c["name"],
                base_dimension=c["base_dimension"],
                rate_limiting=c["rate_limiting"],
                _id=c["_id"],
                meta=c["meta"],
            )
            for c in reg._by_name.values()
        ]

    def __repr__(self) -> str:
        return f"<Consumable: {self.name}>"


__all__ = ["Consumable"]
