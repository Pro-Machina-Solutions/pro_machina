import datetime as dt

from ..exceptions import ForecastError
from ..measures import CustomUnit, SizedDimension
from ..util import as_midnight, parse_datetime
from .products import BatchProduct, ContinuousProduct


class Order:
    def __init__(
        self,
        product: BatchProduct | ContinuousProduct,
        date: dt.date | str,
        qty: SizedDimension,
    ) -> None:
        self.product = product
        self.date = as_midnight(parse_datetime(date))

        if isinstance(qty, CustomUnit):
            pass

        if not product.base_dimension.is_compatible(qty):
            raise ForecastError(
                f"{qty} is not a compatible quantity for {product}"
            )

        self.qty = qty


class DemandForecast:
    def __init__(self) -> None:
        self._orders: list[Order] = []

    def add_order(self, order: Order) -> None:
        self._orders.append(order)


class MadeToStock:
    pass
