from itertools import count

from ..measures import UnsizedDimension


class Consumable:
    _ids = count(1_000_000)

    def __init__(self, name: str, base_dimension: UnsizedDimension) -> None:
        self._id: int = next(self._ids)
        self.name: str = name
        self.base_dimension = base_dimension

    def __repr__(self) -> str:
        return f"<Consumable: {self.name}>"
