from __future__ import annotations

from abc import ABC, abstractmethod


class Duration(ABC):
    @abstractmethod
    def to_seconds(self) -> float: ...

    @abstractmethod
    def from_seconds(self, val: float) -> Duration: ...

    @abstractmethod
    def __add__(self, other: Duration) -> Duration: ...

    @abstractmethod
    def __sub__(self, other: Duration) -> Duration: ...

    @abstractmethod
    def __mul__(self, val: float) -> Duration: ...

    @abstractmethod
    def __div__(self, val: float) -> Duration: ...


class Secs(Duration):
    def __init__(self, duration: float) -> None:
        self.duration = duration

    def to_seconds(self) -> float:
        return self.duration

    def from_seconds(self, val: float) -> Secs:
        return Secs(val)

    def __add__(self, other: Duration) -> Secs:
        return Secs(self.duration + other.to_seconds())

    def __sub__(self, other: Duration) -> Secs:
        return Secs(self.duration - other.to_seconds())

    def __mul__(self, val: float) -> Secs:
        return Secs(self.duration * val)

    def __div__(self, val: float) -> Secs:
        return Secs(duration=self.duration / val)


class Mins(Duration):
    def __init__(self, duration: float) -> None:
        self.duration = duration

    def to_seconds(self) -> float:
        return self.duration * 60

    def from_seconds(self, val: float) -> Mins:
        return Mins(val / 60)

    def __add__(self, other: Duration) -> Mins:
        return self.from_seconds(self.to_seconds() + other.to_seconds())

    def __sub__(self, other: Duration) -> Mins:
        return self.from_seconds(self.to_seconds() - other.to_seconds())

    def __mul__(self, val: float) -> Mins:
        return Mins(self.duration * val)

    def __div__(self, val: float) -> Mins:
        return Mins(duration=self.duration / val)


class Hours(Duration):
    def __init__(self, duration: float) -> None:
        self.duration = duration

    def to_seconds(self) -> float:
        return self.duration * 3600

    def from_seconds(self, val: float) -> Hours:
        return Hours(val / 36000)

    def __add__(self, other: Duration) -> Hours:
        return self.from_seconds(self.to_seconds() + other.to_seconds())

    def __sub__(self, other: Duration) -> Hours:
        return self.from_seconds(self.to_seconds() - other.to_seconds())

    def __mul__(self, val):
        return Hours(self.duration * val)

    def __div__(self, val: float):
        return Hours(duration=self.duration / val)
