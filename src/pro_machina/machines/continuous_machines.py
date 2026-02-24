from itertools import count

from pro_machina.products import ContinuousProduct


class ContinuousMachine:
    _ids = count(0)

    def __init__(self, name: str):
        self._id: int = next(self._ids)
        self.name: str = name

        self._products: list[ContinuousProduct] = []
        self._shifts = []

    def add_product(
        self, product: ContinuousProduct | list[ContinuousProduct]
    ):
        if isinstance(product, ContinuousProduct):
            product = [product]

        if not all(isinstance(item, ContinuousProduct) for item in product):
            raise TypeError(
                "Invalid Product type added to Machine: {self.name}"
            )

        self._products.extend(product)
