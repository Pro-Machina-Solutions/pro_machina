from itertools import count

from pro_machina.products import BatchProduct


class BatchMachine:
    _ids = count(0)

    def __init__(self, name: str):
        self._id = next(self._ids)
        self.name = name

        self._products = []
        self._shifts = []

    def add_product(self, product: BatchProduct | list[BatchProduct]):
        if isinstance(product, BatchProduct):
            product = [product]

        if not all(isinstance(item, BatchProduct) for item in product):
            raise TypeError(
                "Invalid Product type added to Machine: {self.name}"
            )

        self._products.extend(product)
