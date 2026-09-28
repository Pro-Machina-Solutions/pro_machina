from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import ProductError
from .util import Singleton

if TYPE_CHECKING:
    from .problem.consumables import ConsID, Consumable
    from .problem.products import ProdID, _Product
    from .suppliers import Supplier, SupplierID


class ConsumableReg(metaclass=Singleton):
    def __init__(self) -> None:
        self._by_name: dict[tuple[str, str], Consumable] = {}
        self._by_id: dict[ConsID, Consumable] = {}

    def add(self, cons: Consumable) -> None:
        self._by_name[(cons.name, cons.code)] = cons
        self._by_id[cons._id] = cons

    def contains(self, cons: Consumable) -> bool:
        return cons._id in self._by_id

    def get_by_id(self, cons_id: ConsID) -> Consumable:
        return self._by_id[cons_id]


class ProductReg(metaclass=Singleton):
    def __init__(self) -> None:
        self.products_by_id: dict[ProdID, _Product] = {}
        self.products_by_name: dict[tuple[str, str], _Product] = {}

    def contains(self, product: _Product) -> bool:
        return product._id in self.products_by_id

    def add(self, product: _Product) -> None:
        if self.contains(product):
            raise ProductError("Cannot add the product twice to registry")
        elif (product.name, product.code) in self.products_by_name:
            raise ProductError(
                "Name and code combinations for products must be unique"
            )
        else:
            self.products_by_id[product._id] = product
            self.products_by_name[(product.name, product.code)] = product


class ProductGroupReg(metaclass=Singleton):
    pass


class MachineReg(metaclass=Singleton):
    pass


class MachineGroupReg(metaclass=Singleton):
    pass


class LocationReg(metaclass=Singleton):
    pass


class SupplierReg(metaclass=Singleton):
    def __init__(self) -> None:
        self._by_name: dict[tuple[str, str], Supplier] = {}
        self._by_id: dict[SupplierID, Supplier] = {}

    def add(self, sup: Supplier) -> None:
        self._by_name[(sup.name, sup.code)] = sup
        self._by_id[sup._id] = sup

    def contains(self, sup: Supplier) -> bool:
        return sup._id in self._by_id

    def get_by_id(self, sup_id: SupplierID) -> Supplier:
        return self._by_id[sup_id]

    def get_by_name(self, name, code) -> Supplier:
        return self._by_name[(name, code)]


class StorageReg(metaclass=Singleton):
    pass
