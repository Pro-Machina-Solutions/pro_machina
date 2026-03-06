from itertools import count

from ..measures import UnsizedDimension


class Consumable:
    _ids = count(0)

    def __init__(self, name: str, base_dimension: UnsizedDimension) -> None:
        self._id: int = next(self._ids)
        self.name: str = name
        self.base_dimension = base_dimension
