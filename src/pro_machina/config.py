from secrets import randbelow

import u


class Config:
    def __init__(
        self,
        silence_warnings: bool = False,
        base_time_unit: u.Duration = u.minute,
    ) -> None:
        self.silence_warnings: bool = silence_warnings
        self.base_time_unit = base_time_unit

        self._max_iterations: int | None = None
        self._max_runtime: u.Duration | None = None
        self._timebucket_mins: u.Duration | None = 15
        self._random_seed = randbelow(4294967296)

    @property
    def max_iterations(self) -> int | None:
        return self._max_iterations

    @max_iterations.setter
    def max_iterations(self, iterations) -> None:
        if iterations is not None and iterations <= 0:
            raise ValueError("Max iterations must be positive")
        self._max_iterations = iterations

    @property
    def max_runtime(self) -> u.Duration | None:
        return self._max_iterations

    @max_runtime.setter
    def max_runtime(self, runtime: u.Duration) -> None:
        if runtime is not None and runtime <= 0:
            raise ValueError("Max runtime seconds must be positive")
        self._max_runtime = runtime

    @property
    def timebucket_mins(self) -> u.Duration | None:
        return self._max_iterations

    @timebucket_mins.setter
    def timebucket_mins(self, timebucket_mins: u.Duration) -> None:
        if timebucket_mins <= 0:
            raise ValueError("Timebucket mins must be positive")
        self._timebucket_mins = timebucket_mins

    @property
    def random_seed(self) -> int:
        return self._random_seed

    @random_seed.setter
    def random_seed(self, seed: int) -> None:
        if not 0 <= seed <= 4294967295:
            raise ValueError(
                "The random seed must be between 0 and 4294967295 "
                "(the maximum unsigned 32-Bit integer, due to numpy overflow)"
            )
        self._random_seed = seed

    def __repr__(self) -> str:
        return "Hello"
