import datetime as dt
from decimal import Decimal

import numpy as np
import numpy.typing as npt

from ..config import Config
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

        self._prod_demands: dict[int, npt.NDArray[np.float64]] = {}
        self._cons_demands: dict[int, npt.NDArray[np.float64]] = {}

    def add_order(self, order: Order) -> None:
        self._orders.append(order)

    def _sum_demand(
        self,
        aggregator: dict[int, npt.NDArray[np.float64]],
        order: Order,
        _id: int,
        num_buckets: int,
        start_date: dt.datetime,
        horizon_secs: int,
        timebucket_secs: int,
        deflt_num_horizon_buckets: int,
        multiplier: Decimal = Decimal(1),
    ):
        # Have we seen this product before? If not, fill it out with zero
        # base demand for the whole problem
        if _id not in aggregator:
            aggregator[_id] = np.zeros(num_buckets)

        # Determine the start bucket of the order. If it comes before the
        # start date of the problem, then we need to bump it up to match
        theo_start = order.date - dt.timedelta(seconds=horizon_secs)
        if theo_start < start_date:
            theo_start = start_date
            demand_buckets = int(
                (order.date - start_date).total_seconds() / timebucket_secs
            )
            start_index = 0
            end_index = demand_buckets
        else:
            start_index = int(
                (
                    (order.date - dt.timedelta(seconds=horizon_secs))
                    - start_date
                ).total_seconds()
                / timebucket_secs
            )
            end_index = int(start_index + deflt_num_horizon_buckets)
            demand_buckets = int(deflt_num_horizon_buckets)

        demand_per_bucket = float(
            (order.qty._base_qty * multiplier) / Decimal(demand_buckets)
        )
        aggregator[_id][start_index:end_index] += demand_per_bucket

    def _build(
        self, start_date: dt.datetime, end_date: dt.datetime, config: Config
    ):

        timebucket_secs = config._timebucket.to_seconds()
        tot_problem_secs = (end_date - start_date).total_seconds()
        num_buckets = int(tot_problem_secs / timebucket_secs)

        horizon_secs = config.demand_horizon.to_seconds()
        deflt_num_horizon_buckets = horizon_secs / timebucket_secs

        for order in self._orders:
            self._sum_demand(
                aggregator=self._prod_demands,
                order=order,
                _id=order.product._id,
                num_buckets=num_buckets,
                start_date=start_date,
                horizon_secs=int(horizon_secs),
                timebucket_secs=int(timebucket_secs),
                deflt_num_horizon_buckets=int(deflt_num_horizon_buckets),
            )

            for subproduct_id, qty in order.product._bom_products.items():
                self._sum_demand(
                    aggregator=self._prod_demands,
                    order=order,
                    _id=subproduct_id,
                    num_buckets=num_buckets,
                    start_date=start_date,
                    horizon_secs=int(horizon_secs),
                    timebucket_secs=int(timebucket_secs),
                    deflt_num_horizon_buckets=int(deflt_num_horizon_buckets),
                    multiplier=qty,
                )
            for consumable_id, qty in order.product._bom_consumables.items():
                self._sum_demand(
                    aggregator=self._cons_demands,
                    order=order,
                    _id=consumable_id,
                    num_buckets=num_buckets,
                    start_date=start_date,
                    horizon_secs=int(horizon_secs),
                    timebucket_secs=int(timebucket_secs),
                    deflt_num_horizon_buckets=int(deflt_num_horizon_buckets),
                    multiplier=qty,
                )

        for k, v in self._prod_demands.items():
            self._prod_demands[k] = v.cumsum()

        for k, v in self._cons_demands.items():
            self._cons_demands[k] = v.cumsum()


class MadeToStock:
    pass
