from itertools import count


class Consumable:
    _ids = count(0)

    def __init__(
        self,
        name: str,
    ) -> None:
        self._id: int = next(self._ids)
        self.name: str = name
