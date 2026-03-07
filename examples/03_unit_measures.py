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
Bag = CustomUnit("Bag", Unit)
Bag.size_for(sugar, Kilo(0.250))
Bag.size_for(starch, Kilo(1.2))

Bottle = CustomUnit("Bottle", Unit)
Bottle.size_for(rasp_flav, Litre("2.5"))

Roll = CustomUnit("Roll", Unit)
Roll.size_for(wrapper, Sq_Metre(10))

# Our product
prod_1 = ContinuousProduct("Sweet", Unit(10))

prod_1.add_consumable(consumable=sugar, qty=Kilo("7.2"), per=Unit(1000))
prod_1.add_consumable(consumable=starch, qty=Gram(2))
prod_1.add_consumable(consumable=rasp_flav, qty=Bottle(1), per=Unit(20000))
prod_1.add_consumable(consumable=wrapper, qty=Sq_Centimetre(9))
for row in prod_1.consumables:
    print(row)

# Try something that isn't made in Unit quantities
