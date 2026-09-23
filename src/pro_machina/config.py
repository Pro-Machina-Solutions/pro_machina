from __future__ import annotations

from enum import StrEnum
from secrets import randbelow

from .costs import Currency, CurrencyRefresh
from .durations import Duration, Hours, Mins, Secs, Weeks


class InventoryDrawdown(StrEnum):
    FIFO = "First In, First Out"
    LIFO = "Last In, First Out"
    AVE = "Average"


class Config:
    """Set the algorithmic properties for the solver

    Parameters
    ----------
    base_time_unit : type[Duration], optional
        The fundamental time unit of the solver, by default Secs. For now,
        other base units are not supported and this parameter is included as a
        TODO reminder that operating on larger time scales may be more
        efficient for the solver.
    max_iterations : int | None
        Set the maximum number of iterations that the solver will use to
        converge on a solution. This can be used as a measure of early
        termination, regardless of whether the solution has converged or not.
        By default, this is set to None, which will allow the solver to
        terminate naturally once convergence criteria are met.
    max_runtime : Duration | None
        Set the maximum wall clock time on the solver. The solver will stop
        searching for a solution once this threshold is exceeded, regardless of
        whether the solution has converged or not. By default, this is set to
        None, which will allow the solver to terminate naturally once
        convergence criteria are met.
    improvement_threshold_pct : int
        The percentage change in solution costs over N number of iterations
        (`improvement_threshold_iterations`) before the problem is considered
        converged for the purposes of early termination. For example, the
        default is 1%. If the solution cost doesn't improve by more than 1%
        over `improvement_threshold_iterations`, the solver can terminate
        early. By default, 1%.
    improvement_threshold_iterations : int
        How many iterations are performed to check for
        `improvement_threshold_pct` being before the algorithm terminates
        early.
    timebucket : Duration
        The duration span of the problem needs to be broken down into distinct
        buckets with a set duration. Most problems do not need second-by-second
        granularity in the solution, so production periods can be aggregated up
        into a larger unit. By default, production is considered in 15 minute
        "buckets". The larger the bucket size, the quicker the algorithm will
        converge but this comes with a reduction in overall efficiency because
        there is less flexibility in the final schedule, which might lead to
        gross overproduction or avoidable underproduction.

        For example, setting this to Hours(4) means that a machine either runs
        for an additional four hours to make up a small shortfall in supply, or
        doesn't run at all and misses the target. However, perhaps it could
        meet the demand by running just an additional 30 minutes, but that
        option is off the table in this scenario.
    random_seed : int
        Set a random seed between 0 and 4294967296 to make the algorithm
        consistent between runs. Otherwise, the number will be chosen at random
        on each run.
    min_default_swap_block : Duration
        For Continuous problems, we want to have some sensible production runs
        to prevent a machine swapping product every 15 minutes. This sets a
        global lower bound for a production run, which can later be overridden
        by specific constraints if needed. By default this is 4 hours meaning
        that, in the absence of specific constraints, no production run of a
        product of less than 4 hours will appear in the solution.
    max_default_swap_block : Duration
        Similar to min_default_swap_block, we want to set an upper bound on the
        length of a production run in any one swap in the solution search. By
        default this is set to 12 hours. It is important to note that this does
        NOT mean that a production run of a single product will be limited to
        12 hours and then the machine **must** switch to a different product.
        What it does mean is that, in any single swap during the solution
        search, no production run of greater than 12 hours will be inserted
        into the schedule. However, in the final solution, it is still
        perfectly possible that multiple 12 hour blocks of production of the
        same product will be stacked together, effectively becoming a single,
        continuous run.

        If you want to force a maximum production run such that these blocks
        cannot be stacked in arbitrary length runs then you will need to set a
        MaxProductionTime constraint instead.
    demand_horizon : Duration
        Set the default time horizon to consider production for an upcoming
        order or made-to-stock target. For example, if you have an order due on
        15th May 2026 and leave this as Weeks(1) (the default) then the demand
        will be seen by the algorithm starting on 8th of May and ramping up
        linearly from there. Any overproduction during this period will not be
        penalised.

        Scenario: You have an order for 20 pallets of product due on 15th May.
        If the solver can find a solution that clears all of this demand on the
        8th May, meaning that you have all of the pallets lying around for a
        week, this will not be penalised. Any excess production for that order
        before 8th May will incur soft constraint penalties for storage costs.

        This can be overridden by constraints, such as seeing demand for
        particular products needed for seasonal or promotional periods and
        having more-flexible rules on stockpiling. This is just the default for
        products that do not carry any kind of specific contraint.
    base_currency : Currency
        The primary currency for all financial calculations. By default, NON.
        This is a special currency that will value everything relative to their
        base unit quantity as opposed to any particular currency. This allows
        the model to add a cost to solutions even in the absence of factual
        currency data (although the results will be vastly improved if this is
        changed to reflect actual financial value in currencies).

        Items listed in currencies other than the base currency will first be
        converted into the base currency for the purpose of cost calculations
        for solving and reporting.

        Available currencies can be seen with:

        ```python
        from pro_machina.financies import Currencies

        Currencies.list_all()
        ```
    currency_refresh_frequency : CurrencyRefresh
        Determine how requently the conversion rates of currencies are set. By
        default, Daily.
    inventory_drawdown : InventoryDrawdown
        The order and costing of how inventory is used in the production chain
        from consumables through to finished products for sale. By default,
        this is assumed to be the average value of each SKU being held, which
        assumes that the site performs an informal stock rotation.

        Other settings include First In, First Out (FIFO) which ensures that
        the oldest stock is always used before newer stock. This is the
        opposite of First In, Last Out (FILO) in which the newest stock
        available will always be used before the oldest stock.
    """

    def __init__(
        self,
        base_time_unit: type[Duration] = Secs,
    ) -> None:

        self.base_time_unit = base_time_unit

        # Algorithm parameters
        self._max_iterations: int | None = None
        self._max_runtime: Duration | None = None
        self._improvement_threshold_pct: float = 1.0
        self._improvement_threshold_iterations: int = 1000
        self._timebucket: Duration = Mins(15)
        self._random_seed: int = randbelow(4294967296)
        self._min_default_swap_block: Duration = Hours(4)
        self._max_default_swap_block: Duration = Hours(12)
        self._demand_horizon: Duration = Weeks(1)

        # Financials
        self._base_currency = Currency.NON
        self._currency_refresh_frequency: CurrencyRefresh = (
            CurrencyRefresh.DAILY
        )

        # Global Sstock handling
        self._inventory_drawdown: InventoryDrawdown = InventoryDrawdown.AVE

    @property
    def max_iterations(self) -> int | None:
        return self._max_iterations

    @max_iterations.setter
    def max_iterations(self, iterations: int) -> None:
        iterations = int(iterations)
        if iterations is not None and iterations <= 0:
            raise ValueError("Max iterations must be positive")
        self._max_iterations = iterations

    @property
    def max_runtime(self) -> Duration | None:
        return self._max_runtime

    @max_runtime.setter
    def max_runtime(self, runtime: Duration) -> None:
        if runtime is not None and runtime.to_seconds() <= 0:
            raise ValueError("Max runtime duration must be positive")
        self._max_runtime = runtime

    @property
    def improvement_threshold_pct(self) -> float:
        return self._improvement_threshold_pct

    @improvement_threshold_pct.setter
    def improvement_threshold_pct(self, pct: float) -> None:
        pct = float(pct)
        if 0 <= pct <= 100:
            raise ValueError(
                "Improvement threshold pct must be above 0.0 and below 100.0"
            )
        self._improvement_threshold_pct = pct

    @property
    def improvement_threshold_iterations(self) -> float:
        return self._improvement_threshold_iterations

    @improvement_threshold_iterations.setter
    def improvement_threshold_iterations(self, iterations: int) -> None:
        iterations = int(iterations)
        if iterations <= 0:
            raise ValueError(
                "Improvement threshold iterations must be above 0"
            )
        self._improvement_threshold_iterations = iterations

    @property
    def timebucket(self) -> Duration:
        return self._timebucket

    @timebucket.setter
    def timebucket(self, timebucket: Duration) -> None:
        if timebucket.to_seconds() <= 0:
            raise ValueError("Timebucket duration must be positive")
        self._timebucket = timebucket

    @property
    def random_seed(self) -> int:
        return self._random_seed

    @random_seed.setter
    def random_seed(self, seed: int) -> None:
        if not 0 <= seed <= 4294967295:
            raise ValueError(
                "The random seed must be between 0 and 4294967295"
                " (the maximum unsigned 32-Bit integer, due to numpy overflow)"
            )
        self._random_seed = seed

    @property
    def min_default_swap_block(self) -> Duration:
        return self._min_default_swap_block

    @min_default_swap_block.setter
    def min_default_swap_block(self, duration: Duration) -> None:
        if duration.to_seconds() <= 0:
            raise ValueError("Default min duration must be a positive")
        self._min_default_swap_block = duration

    @property
    def max_default_swap_block(self) -> Duration:
        return self._max_default_swap_block

    @max_default_swap_block.setter
    def max_default_swap_block(self, duration: Duration) -> None:
        if duration.to_seconds() <= 0:
            raise ValueError("Default max duration must be a positive")
        self._max_default_swap_block = duration

    @property
    def demand_horizon(self) -> Duration:
        return self._demand_horizon

    @demand_horizon.setter
    def demand_horizon(self, horizon: Duration) -> None:
        if horizon.to_seconds() <= 0:
            raise ValueError("Demand horizon must be a positive duration")
        self._demand_horizon = horizon

    @property
    def base_currency(self) -> str:
        return self._base_currency

    @base_currency.setter
    def base_currency(self, currency: Currency) -> None:
        try:
            self._base_currency = currency
        except AttributeError as e:
            e.add_note("Currency not recognised")
            raise

    @property
    def currency_refresh_frequency(self) -> str:
        return self._currency_refresh_frequency

    @currency_refresh_frequency.setter
    def currency_refresh_frequency(self, freq: CurrencyRefresh) -> None:
        try:
            self._currency_refresh_frequency = freq
        except AttributeError as e:
            e.add_note("Currency refresh frequency not recognised")
            raise
