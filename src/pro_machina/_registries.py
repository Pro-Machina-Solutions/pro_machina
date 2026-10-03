from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import ConsumableError, ProductError
from .util import Singleton

if TYPE_CHECKING:
    from .businesses import Customer, CustomerID, Supplier, SupplierID
    from .measures import CustomUnit, UnitID, UnitName
    from .problem.consumables import ConsID, Consumable
    from .problem.products import ProdID, ProdName, _Product


class UnitReg(metaclass=Singleton):
    """Index of every CustomUnit, for lookup by id/name (e.g. serialising).

    It holds no sizing data - that lives on each CustomUnit - so nothing
    needs to reach in here to work out quantities.
    """

    def __init__(self) -> None:
        self._by_id: dict[UnitID, CustomUnit] = {}
        self._by_name: dict[UnitName, CustomUnit] = {}

    def add(self, unit: CustomUnit) -> None:
        self._by_id[unit._id] = unit
        self._by_name[unit.name] = unit

    def get_by_id(self, unit_id: UnitID) -> CustomUnit:
        return self._by_id[unit_id]

    def get_by_name(self, name: UnitName) -> CustomUnit:
        return self._by_name[name]


class ConsumableReg(metaclass=Singleton):
    def __init__(self) -> None:
        self.cons_by_name: dict[tuple[str, str | None], Consumable] = {}
        self.cons_by_id: dict[ConsID, Consumable] = {}

    def contains(self, cons: Consumable) -> bool:
        return cons._id in self.cons_by_id

    def add(self, cons: Consumable) -> None:
        if self.contains(cons):
            raise ConsumableError("Cannot register same Consumable twice.")
        self.cons_by_name[(cons.name, cons.code)] = cons
        self.cons_by_id[cons._id] = cons

    def get_by_id(self, cons_id: ConsID) -> Consumable:
        rtn = self.cons_by_id.get(cons_id)
        if rtn is None:
            raise ValueError("Consumable ID not recognised.")
        return rtn

    def get_by_name(self, name: str, code: str | None = None) -> Consumable:
        rtn = self.cons_by_name.get((name, code))
        if rtn is None:
            raise ValueError("Consumable name not recognised.")
        return rtn


class ProductReg(metaclass=Singleton):
    def __init__(self) -> None:
        self.prods_by_id: dict[ProdID, _Product] = {}
        self.prods_by_name: dict[tuple[ProdName, str | None], _Product] = {}

    def contains(self, product: _Product) -> bool:
        return product._id in self.prods_by_id

    def add(self, product: _Product) -> None:
        if self.contains(product):
            raise ProductError("Cannot add the product twice to registry")
        elif (product.name, product.code) in self.prods_by_name:
            raise ProductError(
                "Name and code combinations for products must be unique"
            )
        else:
            self.prods_by_id[product._id] = product
            self.prods_by_name[(product.name, product.code)] = product

    def get_by_id(self, prod_id: ProdID) -> _Product:
        rtn = self.prods_by_id.get(prod_id)
        if rtn is None:
            raise ValueError("Product ID not recognised.")
        return rtn

    def get_by_name(self, name: ProdName, code: str | None = None) -> _Product:
        rtn = self.prods_by_name.get((name, code))
        if rtn is None:
            raise ValueError("Product name not recognised.")
        return rtn


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
        self._by_name: dict[tuple[str, str | None], Supplier] = {}
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


class CustomerReg(metaclass=Singleton):
    def __init__(self) -> None:
        self._by_name: dict[tuple[str, str | None], Customer] = {}
        self._by_id: dict[CustomerID, Customer] = {}

    def add(self, cust: Customer) -> None:
        self._by_name[(cust.name, cust.code)] = cust
        self._by_id[cust._id] = cust

    def contains(self, cust: Customer) -> bool:
        return cust._id in self._by_id

    def get_by_id(self, cust_id: CustomerID) -> Customer:
        return self._by_id[cust_id]

    def get_by_name(self, name, code) -> Customer:
        return self._by_name[(name, code)]


class StorageReg(metaclass=Singleton):
    pass
