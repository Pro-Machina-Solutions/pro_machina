import datetime as dt

from ..exceptions import UnitError
from ..measures import SizedDimension
from ..util import parse_datetime
from .products import BatchProduct, Consumable, ContinuousProduct


class StockHolding:
    """Represents the starting stock level of any Products or Consumables

    If theb starting stock of any product or consumable is not set then it will
    be assumed to be zero. In the case of defined consumables, obviously no
    product that depends on that consumable will be possible to produce. This
    may be done deliberately, though, as it may be that you are waiting on a
    delivery (InboundStock) for that particular consumable.

    Parameters
    ----------
    item : ContinuousProduct | BatchProduct | Consumable
        The product or consumable the stock level applies to
    qty : SizedDimension
        The total quantity held at the start of the problem
    """

    def __init__(
        self,
        item: ContinuousProduct | BatchProduct | Consumable,
        qty: SizedDimension,
    ) -> None:

        self._id = item._id
        self.item = item

        if not item.base_dimension.is_compatible(qty):
            raise UnitError(f"{qty} is not a compatible quantity for {item}")
        self.qty = qty


class InboundStock:
    """Represents some inbound delivery of a consumable

    Parameters
    ----------
    item : Consumable
        The consumable being received
    qty : SizedDimension
        The quantity of the consumable
    date : str | dt.datetime
        The date after which this stock will be available for use
    """

    def __init__(
        self, item: Consumable, qty: SizedDimension, date: str | dt.datetime
    ):
        self._id = item._id
        self.item = item

        if not item.base_dimension.is_compatible(qty):
            raise UnitError(f"{qty} is not a compatible quantity for {item}")
        self.qty = qty
        self.date = parse_datetime(date)
