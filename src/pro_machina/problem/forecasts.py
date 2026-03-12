import datetime as dt
from decimal import Decimal

import numpy as np
import numpy.typing as npt

from ..config import Config
from ..durations import Duration, Weeks
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


class MadeToStock:
    def __init__(
        self,
        product: BatchProduct | ContinuousProduct,
        qty: SizedDimension,
        start_date: str | dt.datetime,
        freq: Duration | None = None,
        end_date: str | dt.datetime | None = None,
    ):
        self.start_date = as_midnight(parse_datetime(start_date))

        if not product.base_dimension.is_compatible(qty):
            raise ForecastError(
                f"{qty} is not a compatible quantity for {product}"
            )

        if end_date is not None and freq is None:
            raise ForecastError(
                "Cannot set an end date for MadeToStock without specifying a"
                " frequency of restocking"
            )

        self.product = product
        self.qty = qty
        self.freq = freq
        if end_date is not None:
            self.end_date = parse_datetime(end_date)


class DemandForecast:
    def __init__(self) -> None:
        self._orders: list[Order] = []
        self._made_to_stock: list[MadeToStock] = []

        self._prod_demands: dict[int, npt.NDArray[np.float64]] = {}
        self._cons_demands: dict[int, npt.NDArray[np.float64]] = {}

    def add_order(self, order: Order | MadeToStock) -> None:

        if isinstance(order, Order):
            self._orders.append(order)
        else:
            self._made_to_stock.append(order)

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

    def _process_order_list(
        self,
        order_list: list[Order],
        num_buckets: int,
        start_date: dt.datetime,
        horizon_secs: int,
        timebucket_secs: int,
        deflt_num_horizon_buckets: int,
    ):

        for order in order_list:
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

    def _build(
        self, start_date: dt.datetime, end_date: dt.datetime, config: Config
    ):

        timebucket_secs = config._timebucket.to_seconds()
        tot_problem_secs = (end_date - start_date).total_seconds()
        num_buckets = int(tot_problem_secs / timebucket_secs)

        horizon_secs = config.demand_horizon.to_seconds()
        deflt_num_horizon_buckets = horizon_secs / timebucket_secs

        # First process set orders
        self._process_order_list(
            self._orders,
            num_buckets=num_buckets,
            start_date=start_date,
            horizon_secs=int(horizon_secs),
            timebucket_secs=int(timebucket_secs),
            deflt_num_horizon_buckets=int(deflt_num_horizon_buckets),
        )

        # Now process any made to stock targets
        # The easiest way to do this is to keep raising them as fake orders
        # for the purpose of generating the demand
        mts_orders: list[Order] = []
        for mts in self._made_to_stock:
            if mts.freq is not None and mts.end_date is None:
                # Repeat up until our problem end date
                dates = [mts.start_date]
                running_date = mts.start_date
                while (
                    running_date + dt.timedelta(seconds=mts.freq.to_seconds())
                    < end_date
                ):
                    running_date += dt.timedelta(seconds=mts.freq.to_seconds())
                    dates.append(running_date)

                for date in dates:
                    # These are for complete periods in our solver window
                    mts_orders.append(
                        Order(mts.product, date=date, qty=mts.qty)
                    )

                if running_date < end_date:
                    # Tie up any partial period
                    partial_period = Decimal(
                        (end_date - running_date).total_seconds()
                        / mts.freq.to_seconds()
                    )

                    mts_orders.append(
                        Order(
                            product=mts.product,
                            date=end_date,
                            qty=mts.qty * partial_period,
                        )
                    )

            elif mts.freq is not None and mts.end_date is not None:
                # Repeat up until the specified end date or until our problem
                # end
                dates = [mts.start_date]
                running_date = mts.start_date
                while (
                    running_date + dt.timedelta(seconds=mts.freq.to_seconds())
                    < mts.end_date
                    and running_date
                    + dt.timedelta(seconds=mts.freq.to_seconds())
                    < end_date
                ):
                    running_date += dt.timedelta(seconds=mts.freq.to_seconds())
                    dates.append(running_date)

                for date in dates:
                    # These are for complete periods in our solver window
                    mts_orders.append(
                        Order(mts.product, date=date, qty=mts.qty)
                    )

                if running_date < end_date:
                    # Tie up any partial period. We need to know the earlier of
                    # the specified freqnecy or the global problem end date
                    e_d = mts.end_date if mts.end_date < end_date else end_date
                    partial_period = Decimal(
                        (e_d - running_date).total_seconds()
                        / mts.freq.to_seconds()
                    )

                    mts_orders.append(
                        Order(
                            mts.product,
                            date=e_d,
                            qty=(mts.qty * partial_period),
                        )
                    )

        self._process_order_list(
            mts_orders,
            num_buckets=num_buckets,
            start_date=start_date,
            horizon_secs=int(horizon_secs),
            timebucket_secs=int(timebucket_secs),
            deflt_num_horizon_buckets=int(deflt_num_horizon_buckets),
        )

        for k, v in self._prod_demands.items():
            self._prod_demands[k] = v.cumsum()

        for k, v in self._cons_demands.items():
            self._cons_demands[k] = v.cumsum()
