from secrets import randbelow

from .durations import Duration, Hours, Mins, Secs, Weeks


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
        consistent between runs
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
    """

    def __init__(
        self,
        base_time_unit: type[Duration] = Secs,
    ) -> None:

        self.base_time_unit = base_time_unit

        self._max_iterations: int | None = None
        self._max_runtime: Duration | None = None
        self._timebucket: Duration = Mins(15)
        self._random_seed = randbelow(4294967296)
        self._demand_horizon: Duration = Weeks(1)
        self._default_min_product_block_time: Duration = Hours(4)

    @property
    def max_iterations(self) -> int | None:
        return self._max_iterations

    @max_iterations.setter
    def max_iterations(self, iterations) -> None:
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
    def demand_horizon(self) -> Duration:
        return self._demand_horizon

    @demand_horizon.setter
    def demand_horizon(self, horizon: Duration) -> None:
        if horizon.to_seconds() <= 0:
            raise ValueError("Demand horizon must be a positive duration")
        self._demand_horizon = horizon

    @property
    def default_min_product_block_time(self) -> Duration:
        return self._default_min_product_block_time

    @default_min_product_block_time.setter
    def default_min_product_block_time(self, runtime: Duration) -> None:
        if runtime.to_seconds() <= 0:
            raise ValueError("Default min runtime must be a positive duration")
        self._default_min_product_block_time = runtime

    def __repr__(self) -> str:
        return "Hello"
