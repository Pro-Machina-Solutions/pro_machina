from secrets import randbelow

from .durations import Duration, Mins, Secs, Weeks


class Config:
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

    def __repr__(self) -> str:
        return "Hello"
