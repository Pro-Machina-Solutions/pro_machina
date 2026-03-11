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
        return Hours(val / 3600)

    def __add__(self, other: Duration) -> Hours:
        return self.from_seconds(self.to_seconds() + other.to_seconds())

    def __sub__(self, other: Duration) -> Hours:
        return self.from_seconds(self.to_seconds() - other.to_seconds())

    def __mul__(self, val) -> Hours:
        return Hours(self.duration * val)

    def __div__(self, val: float) -> Hours:
        return Hours(duration=self.duration / val)


class Days(Duration):
    def __init__(self, duration: float) -> None:
        self.duration = duration

    def to_seconds(self) -> float:
        return self.duration * 3600 * 24

    def from_seconds(self, val: float) -> Days:
        return Days(val / (3600 * 24))

    def __add__(self, other: Duration) -> Days:
        return self.from_seconds(self.to_seconds() + other.to_seconds())

    def __sub__(self, other: Duration) -> Days:
        return self.from_seconds(self.to_seconds() - other.to_seconds())

    def __mul__(self, val) -> Days:
        return Days(self.duration * val)

    def __div__(self, val: float) -> Days:
        return Days(duration=self.duration / val)


class Weeks(Duration):
    def __init__(self, duration: float) -> None:
        self.duration = duration

    def to_seconds(self) -> float:
        return self.duration * 3600 * 24 * 7

    def from_seconds(self, val: float) -> Weeks:
        return Weeks(val / (3600 * 24 * 7))

    def __add__(self, other: Duration) -> Weeks:
        return self.from_seconds(self.to_seconds() + other.to_seconds())

    def __sub__(self, other: Duration) -> Weeks:
        return self.from_seconds(self.to_seconds() - other.to_seconds())

    def __mul__(self, val) -> Weeks:
        return Weeks(self.duration * val)

    def __div__(self, val: float) -> Weeks:
        return Weeks(duration=self.duration / val)
