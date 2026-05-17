from itertools import count
from warnings import warn

import pro_machina

from ..machines import _Machine
from ..products import _Product


class ProductGroup:
    _ids = count(0)

    def __init__(self, name: str, products: list[_Product] | None = None):
        self._id = next(self._ids)
        self.name = name
        self.products: list[_Product] = (
            products if products is not None else []
        )

        if self.products:
            if not all(isinstance(item, _Product) for item in self.products):
                raise TypeError("Incorrect type added to product group")

    def add_products(self, products: _Product | list[_Product]):
        if isinstance(products, _Product):
            self.products.append(products)
        else:
            self.products.extend(products)

        prev_len = len(self.products)
        self.products = list(set(self.products))
        if (
            len(self.products) < prev_len
            and not pro_machina.options["silence_warnings"]
        ):
            warn(
                f"\n Duplicate products were added to group: {self.name}\n",
                stacklevel=3,
            )

        if not all(isinstance(item, _Product) for item in self.products):
            raise TypeError("Incorrect type added to product group")


class PairedMachines:
    _ids = count(0)

    def __init__(self, name: str, machines: list[_Machine] | None = None):
        self._id = next(self._ids)
        self.name = name
        self.machines: list[_Machine] = (
            machines if machines is not None else []
        )
        if self.machines:
            if not all(isinstance(item, _Machine) for item in self.machines):
                raise TypeError("Incorrect type added to paired machines")

    def add_machines(self, machines: _Machine | list[_Machine]):
        if isinstance(machines, _Machine):
            self.machines.append(machines)
        else:
            self.machines.extend(machines)

        if not all(isinstance(item, _Machine) for item in self.machines):
            raise TypeError("Incorrect type added to paired machines")

        prev_len = len(self.machines)
        self.products = list(set(self.machines))
        if (
            len(self.machines) < prev_len
            and not pro_machina.options["silence_warnings"]
        ):
            warn(
                f"\n Duplicate machines were added to pairing: {self.name}\n",
                stacklevel=3,
            )


class MutuallyExclusiveMachines:
    _ids = count(0)

    def __init__(self, name: str, machines: list[_Machine] | None = None):
        self._id = next(self._ids)
        self.name = name
        self.machines: list[_Machine] = (
            machines if machines is not None else []
        )
        if self.machines:
            if not all(isinstance(item, _Machine) for item in self.machines):
                raise TypeError(
                    "Incorrect type added to mutually exclusive machines"
                )

    def add_machines(self, machines: _Machine | list[_Machine]):
        if isinstance(machines, _Machine):
            self.machines.append(machines)
        else:
            self.machines.extend(machines)

        if not all(isinstance(item, _Machine) for item in self.machines):
            raise TypeError(
                "Incorrect type added to mutually exclusive machines"
            )

        prev_len = len(self.machines)
        self.products = list(set(self.machines))
        if (
            len(self.machines) < prev_len
            and not pro_machina.options["silence_warnings"]
        ):
            warn(
                "\n Duplicate machines were added to mutually exclusive"
                f" pairing: {self.name}\n",
                stacklevel=3,
            )
