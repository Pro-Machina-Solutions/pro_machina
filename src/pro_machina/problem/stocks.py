import datetime as dt

from pro_machina import BatchProduct, Consumable, ContinuousProduct
from pro_machina.measures import SizedDimension
from pro_machina.util import parse_datetime


class StockHolding:
    def __init__(
        self,
        item: ContinuousProduct | BatchProduct | Consumable,
        qty: SizedDimension,
    ) -> None:
        self._id = item._id
        self.item = item

        if not item.base_dimension.is_compatible(qty):
            raise TypeError(f"{qty} is not a compatible quantity for {item}")
        self.qty = qty


class InboundStock:
    def __init__(
        self, item: Consumable, qty: SizedDimension, date: str | dt.datetime
    ):
        self._id = item._id
        self.item = item

        if not item.base_dimension.is_compatible(qty):
            raise TypeError(f"{qty} is not a compatible quantity for {item}")
        self.qty = qty
        self.date = parse_datetime(date)
