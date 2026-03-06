from pro_machina import Consumable, ContinuousProduct
from pro_machina.measures import (
    Area,
    BaseUnit,
    CustomUnit,
    Gram,
    Kilo,
    Volume,
    Weight,
)

# Define some consumables
sugar = Consumable("sugar", Weight)
starch = Consumable("starch", Weight)
rasp_flav = Consumable("raspberry flavour", Volume)
wrapper = Consumable("red wrapper", Area)

Bag = CustomUnit("bag of sugar", BaseUnit)
Bag.size_for(sugar, Kilo(0.250))

# Our product
prod_a = ContinuousProduct("Sweet", Weight)
prod_a.add_consumable(sugar, Bag(2.5), Kilo(80))
prod_a.add_consumable(starch, Gram(7.2))
print(prod_a.consumables)
