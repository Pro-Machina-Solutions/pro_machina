from __future__ import annotations

import datetime as dt
import warnings
from decimal import Decimal
from itertools import count
from typing import TYPE_CHECKING, NewType, TypedDict

from ._constraints import HardConstraint, SoftConstraint
from .products import ProdID, ProdSubtype, ProductGroup

if TYPE_CHECKING:
    from .problem import Problem

import numpy as np
import numpy.typing as npt

from pro_machina import options

from .._registries import ProductReg
from ..businesses import Customer
from ..costs import OrderValue
from ..durations import Duration
from ..measures import Quantity, resolve_qty
from ..util import (
    as_day_start,
    get_problem_buckets,
)
from .consumables import ConsID

OrderID = NewType("OrderID", int)
MtsID = NewType("MtsID", int)


class Order:
    _ids = count(0)

    def __init__(
        self,
        due_date: dt.date | str,
        name: str | None = None,
        code: str | None = None,
        production_lead_time: Duration | None = None,
        customer: Customer | None = None,
        order_value: OrderValue | None = None,
        lines: Orderline | list[Orderline] | None = None,
        hard_constraints: HardConstraint | list[HardConstraint] | None = None,
        soft_constraints: SoftConstraint | list[SoftConstraint] | None = None,
    ) -> None:
        self._id = OrderID(next(self._ids))
        if name is None and code is None:
            raise ValueError(
                "Either a name or a code must be supplied for an Order."
            )
        self.name = name
        self.code = code
        self.due_date = as_day_start(due_date)
        if (
            production_lead_time is not None
            and production_lead_time.to_seconds() <= 0
        ):
            raise ValueError(
                "An Order's production lead time must be positive."
            )
        self.production_lead_time = production_lead_time

        customer = customer
        order_value = order_value

        self._lines: dict[int, Orderline] = {}
        if lines is not None:
            self.add_orderlines(lines)

        self._hard_constraints: list[HardConstraint] = []
        if hard_constraints is not None:
            self.add_hard_constraints(hard_constraints)

        self._soft_constraints: list[SoftConstraint] = []
        if soft_constraints is not None:
            self.add_soft_constraints(soft_constraints)

    def add_orderlines(self, lines: Orderline | list[Orderline]) -> None:

        if not isinstance(lines, list):
            lines = [lines]

        if not all(isinstance(line, Orderline) for line in lines):
            raise TypeError("Not a valid Orderline type.")

        for line in lines:
            if line._id in self._lines and not options["silence_warnings"]:
                _name = self.name if self.name is not None else self.code
                warnings.warn(
                    (
                        f"Orderline of {line.product.name} has been added more"
                        f" than once to order: {_name}"
                    ),
                    stacklevel=1,
                )
            self._lines[line._id] = line

    def add_hard_constraints(
        self, constraints: HardConstraint | list[HardConstraint]
    ) -> None:

        if not isinstance(constraints, list):
            constraints = [constraints]

        if not all(isinstance(cons, HardConstraint) for cons in constraints):
            raise TypeError("Not a valid HardConstraint type.")

        # TODO

    def add_soft_constraints(
        self, constraints: SoftConstraint | list[SoftConstraint]
    ) -> None:

        if not isinstance(constraints, list):
            constraints = [constraints]

        if not all(isinstance(cons, SoftConstraint) for cons in constraints):
            raise TypeError("Not a valid SoftConstraint type.")

        # TODO


class Orderline:
    _ids = count(0)

    def __init__(self, product: ProdSubtype, qty: Quantity) -> None:

        self._id = next(self._ids)
        self.product = product
        self.qty = resolve_qty(qty, product)


class MadeToStock:
    _ids = count(0)

    def __init__(
        self,
        product: ProdSubtype | ProductGroup,
        qty: Quantity,
        start_date: str | dt.datetime,
        end_date: str | dt.datetime | None = None,
        freq: Duration | None = None,
        hard_constraints: HardConstraint | list[HardConstraint] | None = None,
        soft_constraints: SoftConstraint | list[SoftConstraint] | None = None,
    ):
        self._id = MtsID(next(self._ids))

        if not isinstance(product, (ProductGroup, ProdSubtype)):
            raise TypeError("Not a valid Product or Product group for MTS.")

        self.start_date = as_day_start(start_date)
        if freq is None and end_date is None:
            raise ValueError(
                "Either a frequency or an end date must be specified for"
                " MadeToStock"
            )

        if freq is not None and freq.to_seconds() <= 0:
            raise ValueError("A MadeToStock frequency must be positive.")

        self.end_date = (
            as_day_start(end_date) if end_date is not None else None
        )

        # Validate now - raises if qty isn't a measure, is incompatible, or
        # is a CustomUnit not sized for every product - but keep it
        # unresolved: for a ProductGroup it means a different amount per
        # product.
        members = (
            product._products.values()
            if isinstance(product, ProductGroup)
            else [product]
        )
        for member in members:
            resolve_qty(qty, member)

        self.qty = qty
        self.product = product
        self.freq = freq

        self._hard_constraints: list[HardConstraint] = []
        if hard_constraints is not None:
            self.add_hard_constraints(hard_constraints)

        self._soft_constraints: list[SoftConstraint] = []
        if soft_constraints is not None:
            self.add_soft_constraints(soft_constraints)

    def add_hard_constraints(
        self, constraints: HardConstraint | list[HardConstraint]
    ) -> None:

        if not isinstance(constraints, list):
            constraints = [constraints]

        if not all(isinstance(cons, HardConstraint) for cons in constraints):
            raise TypeError("Not a valid HardConstraint type.")

        # TODO

    def add_soft_constraints(
        self, constraints: SoftConstraint | list[SoftConstraint]
    ) -> None:

        if not isinstance(constraints, list):
            constraints = [constraints]

        if not all(isinstance(cons, SoftConstraint) for cons in constraints):
            raise TypeError("Not a valid SoftConstraint type.")

        # TODO


class _MTSCycle(TypedDict):
    start_index: int
    end_index: int
    proportion: Decimal


class _OrderBucket(TypedDict):
    start_index: int
    end_index: int
    product_demands: dict[ProdID, Decimal]
    consumable_demands: dict[ConsID, Decimal]


class DemandForecast:
    def __init__(
        self,
        orders: Order | list[Order] | None = None,
        mts: MadeToStock | list[MadeToStock] | None = None,
    ) -> None:
        self.orders: list[Order] = []
        self._seen_orders: set[OrderID] = set()
        self.mts: list[MadeToStock] = []
        self._seen_mts: set[MtsID] = set()
        self._seen_mts_products: set[ProdID] = set()

        if orders is not None:
            self.add_order(orders)
        if mts is not None:
            self.add_mts(mts)

        # Containers to be populated at problem build time
        self._prod_demand_buckets: dict[ProdID, npt.NDArray[np.float64]] = {}
        self._cons_demand_buckets: dict[ConsID, npt.NDArray[np.float64]] = {}

    def add_order(self, orders: Order | list[Order]) -> None:

        if isinstance(orders, Order):
            orders = [orders]

        if not all(isinstance(order, Order) for order in orders):
            raise TypeError("Invalid Order type passed.")

        for order in orders:
            if order._id in self._seen_orders:
                _name = order.name if order.name is not None else order.code
                raise ValueError(f"Cannot add the same order: {_name} twice.")
            self.orders.append(order)
            self._seen_orders.add(order._id)

    def add_mts(self, mts: MadeToStock | list[MadeToStock]) -> None:

        if isinstance(mts, MadeToStock):
            mts = [mts]

        if not all(isinstance(m, MadeToStock) for m in mts):
            raise TypeError("Invalid MadeToStock type passed.")

        for m in mts:
            if m._id in self._seen_mts:
                raise ValueError("Cannot raise this MTS order twice")

            if isinstance(m.product, ProdSubtype):
                if m.product._id in self._seen_mts_products:
                    raise ValueError(
                        f"Cannot make a second MTS order for {m.product.name}"
                    )
                self._seen_mts_products.add(m.product._id)

            elif isinstance(m.product, ProductGroup):
                for prod in m.product._products.values():
                    if prod._id in self._seen_mts_products:
                        raise ValueError(
                            f"Cannot make a second MTS order for {prod.name}"
                        )
                    self._seen_mts_products.add(prod._id)

            self.mts.append(m)
            self._seen_mts.add(m._id)

    def _preprocessing(self, problem: Problem) -> None:
        self.problem = problem
        self.prob_start = problem._start
        self.prob_end = problem._end
        self.timebucket = problem.config.timebucket

        self.num_buckets = get_problem_buckets(
            self.prob_start, self.prob_end, self.timebucket
        )
        self.dflt_demand_horizon_secs = (
            problem.config.demand_horizon.to_seconds()
        )

        self.null_demand = np.zeros(shape=self.num_buckets, dtype=np.float64)

    def _window_indices(
        self, start: dt.datetime, end: dt.datetime
    ) -> tuple[int, int, float] | None:
        """Locate the half-open window [start, end) within the problem.

        Every production window is start-inclusive and end-exclusive:
        production can happen at ``start`` but not at ``end``. So:

        - something due on a date gets no production on that date (it must
          already be made by 00:00 that day), and
        - a window that runs past the problem end keeps the problem's last
          day, because the problem itself is [prob_start, prob_end).

        Returns
        -------
        tuple[int, int, float] | None
            ``(start_index, end_index, inside_secs)``: the bucket slice to
            use (``end_index`` is exclusive, so at most ``num_buckets``) and
            how many seconds of the window fall inside the problem. None if
            the window doesn't overlap the problem at all.
        """
        lo = max(start, self.prob_start)
        hi = min(end, self.prob_end)
        if hi <= lo:
            return None

        bucket_secs = self.timebucket.to_seconds()
        lo_secs = (lo - self.prob_start).total_seconds()
        hi_secs = (hi - self.prob_start).total_seconds()

        # Floor the start and ceil the end so a window that isn't aligned to
        # bucket boundaries still covers every bucket it touches
        start_index = int(lo_secs // bucket_secs)
        end_index = min(self.num_buckets, int(-(-hi_secs // bucket_secs)))

        return start_index, end_index, hi_secs - lo_secs

    def _process_order_buckets(self, order: Order) -> _OrderBucket | None:

        lead_secs = (
            order.production_lead_time.to_seconds()
            if order.production_lead_time is not None
            else self.dflt_demand_horizon_secs
        )
        prod_start = order.due_date - dt.timedelta(seconds=lead_secs)

        # Production window is [prod_start, due_date): nothing is made on the
        # due date itself
        window = self._window_indices(prod_start, order.due_date)
        if window is None:
            # Order isn't in our problem time period, including its ramp up
            # time. Just ignore it.
            return None

        start_bucket_index, end_bucket_index, inside_secs = window

        # Share of the order's production window that falls in the problem,
        # spread evenly over the buckets it covers
        in_problem = Decimal(inside_secs) / Decimal(lead_secs)
        num_buckets = end_bucket_index - start_bucket_index

        prod_demand: dict[ProdID, Decimal] = {}
        cons_demand: dict[ConsID, Decimal] = {}

        # Take the product from each line (an order may hold several lines
        # for the same product, so demand accumulates)
        for line in order._lines.values():
            _prod = line.product
            base_qty_per_bucket = line.qty._base_qty * in_problem / num_buckets
            prod_demand[_prod._id] = (
                prod_demand.get(_prod._id, 0) + base_qty_per_bucket
            )

            # Account for any subproducts
            for subprod_id, demand in _prod._bom_products.items():
                prod_demand[subprod_id] = prod_demand.get(subprod_id, 0) + (
                    base_qty_per_bucket * demand
                )

            # Now account for consumables
            for cons_id, demand in _prod._bom_consumables.items():
                cons_demand[cons_id] = cons_demand.get(cons_id, 0) + (
                    base_qty_per_bucket * demand
                )

        return _OrderBucket(
            start_index=start_bucket_index,
            end_index=end_bucket_index,
            product_demands=prod_demand,
            consumable_demands=cons_demand,
        )

    def _process_orders(self) -> None:
        for order in self.orders:
            res = self._process_order_buckets(order=order)
            if res is None:
                continue
            for prod_id, demand in res["product_demands"].items():
                if prod_id not in self._prod_demand_buckets:
                    base = self.null_demand.copy()
                    base[res["start_index"] : res["end_index"]] = demand
                    self._prod_demand_buckets[prod_id] = base
                else:
                    self._prod_demand_buckets[prod_id][
                        res["start_index"] : res["end_index"]
                    ] += float(demand)

            for cons_id, demand in res["consumable_demands"].items():
                if cons_id not in self._cons_demand_buckets:
                    base = self.null_demand.copy()
                    base[res["start_index"] : res["end_index"]] = demand
                    self._cons_demand_buckets[cons_id] = base
                else:
                    self._cons_demand_buckets[cons_id][
                        res["start_index"] : res["end_index"]
                    ] += float(demand)

    def _decipher_mts_cycle(self, mts: MadeToStock) -> list[_MTSCycle] | None:
        """Split an MTS into production windows and place them in the problem.

        Each window is half-open, [start, end), like an order's production
        window (see _window_indices). Its ``proportion`` is the share of that
        window's full MTS quantity that has to be made inside the problem.

        - One-off (no freq): a single window [start_date, end_date).
        - Recurring: windows of length freq starting from start_date. The
          last one is cut short by end_date if that falls mid-cycle.

        Returns None if no window overlaps the problem.
        """
        # (window start, window end, seconds that the full quantity spans)
        windows: list[tuple[dt.datetime, dt.datetime, float]] = []

        if mts.freq is None:
            # This should be caught separately in constructor of MadeToStock
            assert mts.end_date is not None
            windows.append(
                (
                    mts.start_date,
                    mts.end_date,
                    (mts.end_date - mts.start_date).total_seconds(),
                )
            )
        else:
            cycle = dt.timedelta(seconds=mts.freq.to_seconds())
            stop = (
                self.prob_end
                if mts.end_date is None
                else min(mts.end_date, self.prob_end)
            )

            # Skip whole cycles that finish before the problem starts
            cycle_start = mts.start_date
            if cycle_start < self.prob_start:
                skipped = (self.prob_start - cycle_start) // cycle
                cycle_start += cycle * skipped

            while cycle_start < stop:
                cycle_end = cycle_start + cycle
                if mts.end_date is not None and mts.end_date < cycle_end:
                    # Final cycle cut short by the MTS end date: the full
                    # quantity is made over the shortened window, as for a
                    # one-off MTS
                    windows.append(
                        (
                            cycle_start,
                            mts.end_date,
                            (mts.end_date - cycle_start).total_seconds(),
                        )
                    )
                else:
                    windows.append(
                        (cycle_start, cycle_end, cycle.total_seconds())
                    )
                cycle_start = cycle_end

        cycle_demands: list[_MTSCycle] = []
        for start, end, full_secs in windows:
            placed = self._window_indices(start, end)
            if placed is None:
                continue
            start_index, end_index, inside_secs = placed
            cycle_demands.append(
                _MTSCycle(
                    start_index=start_index,
                    end_index=end_index,
                    proportion=Decimal(inside_secs) / Decimal(full_secs),
                )
            )

        return cycle_demands or None

    def _process_mts(self) -> None:
        prod_reg = ProductReg()

        for mts in self.mts:
            # First we need to resolve the units for all products in MTS
            resolved_qtys: dict[ProdID, Decimal] = {}

            if isinstance(mts.product, ProdSubtype):
                tot_demand = resolve_qty(mts.qty, mts.product)._base_qty
                resolved_qtys[mts.product._id] = tot_demand
            else:
                # Need to cycle through all products in group
                for product in mts.product._products.values():
                    tot_demand = resolve_qty(mts.qty, product)._base_qty
                    resolved_qtys[product._id] = tot_demand

            # Now go through the individual cycles
            cycles = self._decipher_mts_cycle(mts)

            if cycles is None:
                # Outside of problem date range
                continue

            for cycle in cycles:
                for prod_id, tot_demand in resolved_qtys.items():
                    problem_demand = tot_demand * cycle["proportion"]
                    buckets = cycle["end_index"] - cycle["start_index"]
                    per_bucket = problem_demand / buckets
                    if prod_id not in self._prod_demand_buckets:
                        self._prod_demand_buckets[prod_id] = (
                            self.null_demand.copy()
                        )

                    self._prod_demand_buckets[prod_id][
                        cycle["start_index"] : cycle["end_index"]
                    ] += float(per_bucket)

                    _prod = prod_reg.get_by_id(prod_id)

                    # Account for any subproducts
                    for subprod_id, demand in _prod._bom_products.items():
                        if subprod_id not in self._prod_demand_buckets:
                            self._prod_demand_buckets[subprod_id] = (
                                self.null_demand.copy()
                            )
                        self._prod_demand_buckets[subprod_id][
                            cycle["start_index"] : cycle["end_index"]
                        ] += float(per_bucket * demand)

                    # Now account for consumables
                    for cons_id, demand in _prod._bom_consumables.items():
                        if cons_id not in self._cons_demand_buckets:
                            self._cons_demand_buckets[cons_id] = (
                                self.null_demand.copy()
                            )
                        self._cons_demand_buckets[cons_id][
                            cycle["start_index"] : cycle["end_index"]
                        ] += float(per_bucket * demand)

    def _build(self, problem: Problem) -> None:
        self._preprocessing(problem)
        self._process_orders()
        self._process_mts()


__all__ = ["DemandForecast", "MadeToStock", "Order", "Orderline"]
