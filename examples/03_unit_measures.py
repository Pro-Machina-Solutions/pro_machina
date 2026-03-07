from pro_machina import Consumable, ContinuousProduct
from pro_machina.measures import (
    Area,
    CustomUnit,
    Gram,
    Kilo,
    Litre,
    Sq_Centimetre,
    Sq_Metre,
    Unit,
    Volume,
    Weight,
)

# Define some consumables
sugar = Consumable("sugar", Weight)
starch = Consumable("starch", Weight)
rasp_flav = Consumable("raspberry flavour", Volume)
wrapper = Consumable("red wrapper", Area)

# Custom units we buy the consumables in
Bag = CustomUnit("bag", Unit)
Bag.size_for(sugar, Kilo(0.250))
Bag.size_for(starch, Kilo(1.2))

Bottle = CustomUnit("Bottle", Volume)
Bottle.size_for(rasp_flav, Litre("2.5"))

Roll = CustomUnit("Roll", Area)
Roll.size_for(wrapper, Sq_Metre(10))

# Our product
prod_1 = ContinuousProduct("Sweet", Weight)

prod_1.add_consumable(sugar, Gram("7.2"))
prod_1.add_consumable(starch, Gram(2))
prod_1.add_consumable(rasp_flav, Bottle(1), Kilo(20))
prod_1.add_consumable(wrapper, Sq_Centimetre(3))
print(prod_1.consumables)
