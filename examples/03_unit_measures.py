from pro_machina import Consumable, ContinuousProduct
from pro_machina.measures import (
    Area,
    BaseUnit,
    CustomUnit,
    FluidVolume,
    Gram,
    Kilo,
    Litre,
    Millilitre,
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
Bag = CustomUnit("Bag", BaseUnit)
Bag.size_for(sugar, Kilo(0.250))
Bag.size_for(starch, Kilo(1.2))

Bottle = CustomUnit("Bottle", BaseUnit)
Bottle.size_for(rasp_flav, Litre("2.5"))

Roll = CustomUnit("Roll", BaseUnit)
Roll.size_for(wrapper, Sq_Metre(10))

# Our product
prod_1 = ContinuousProduct("Sweet", BaseUnit)

prod_1.add_consumable(consumable=sugar, qty=Kilo("7.2"), per=Unit(1000))
prod_1.add_consumable(consumable=starch, qty=Gram(2), per=Unit(1))
prod_1.add_consumable(consumable=rasp_flav, qty=Bottle(1), per=Unit(20000))
prod_1.add_consumable(consumable=wrapper, qty=Sq_Centimetre(9), per=Unit(1))
for row in prod_1.consumables:
    print(row)

print("###########")

# Try something that isn't made in Unit quantities
goopTM = ContinuousProduct("Goop (TM)", FluidVolume)
goopTM.add_consumable(consumable=sugar, qty=Kilo("0.5"), per=Litre(1))
goopTM.add_consumable(consumable=starch, qty=Kilo(20), per=Litre(250))
goopTM.add_consumable(consumable=rasp_flav, qty=Millilitre(19), per=Litre(2))
for row in goopTM.consumables:
    print(row)
