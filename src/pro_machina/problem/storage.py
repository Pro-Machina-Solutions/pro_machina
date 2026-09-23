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
    ):
        super().__init__(name=name)
