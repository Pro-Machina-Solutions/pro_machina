from pro_machina import Consumable, ContinuousProduct
from pro_machina.measures import (
    Area,
    CustomUnit,
    Gram,
    Kilo,
    Unit,
    Volume,
    Weight,
)

# Define some consumables
sugar = Consumable("sugar", Weight)
starch = Consumable("starch", Weight)
rasp_flav = Consumable("raspberry flavour", Volume)
wrapper = Consumable("red wrapper", Area)

Bag = CustomUnit("bag of sugar", Unit)
Bag.size_for(sugar, Kilo(0.250))
Bag.size_for(starch, Kilo(1.2))

# Our product
prod_a = ContinuousProduct("Sweet", Weight)
prod_a.add_consumable(sugar, Bag("2"), Kilo(80))
prod_a.add_consumable(starch, Bag("0.1"), Gram(110))
print(prod_a.consumables)
