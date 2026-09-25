from __future__ import annotations

from ..measures import CustomUnit, SizedDimension
from .consumables import Consumable


class _Storage:
    def __init__(self, name: str):
        self.name = name


class TempStorage(_Storage):
    """Unbounded generic storage e.g. just assume it's available"""

    def __init__(self, name: str):
        super().__init__(name=name)


class StoreRoom(_Storage):
    def __init__(self, name: str):
        super().__init__(name=name)


class ConsumableStorage(_Storage):
    """e.g. sugar silos"""

    def __init__(
        self,
        name: str,
        consumables: Consumable | list[Consumable] | None = None,
        max_capacity: SizedDimension | CustomUnit | None = None,
    ):
        super().__init__(name=name)

        if consumables is not None:
            self._set_consumables(consumables)

    def _set_consumables(self, consumables: Consumable | list[Consumable]):
        if isinstance(consumables, Consumable):
            consumables = [consumables]

        if not all(isinstance(item, Consumable) for item in consumables):
            raise TypeError("Invalid Consumable type specified")
