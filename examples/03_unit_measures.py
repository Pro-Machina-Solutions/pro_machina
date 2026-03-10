from pro_machina import Config, Consumable, ContinuousProduct
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
    Weight,
)

config = Config()
config.random_seed = 42
# config.silence_warnings = True

# Define some consumables
sugar = Consumable("sugar", Weight)
starch = Consumable("starch", Weight)
rasp_flav = Consumable("raspberry flavour", FluidVolume)
apple_flav = Consumable("apple flavour", FluidVolume)
wrapper = Consumable("red wrapper", Area)

# Custom units we buy the consumables in
Bag = CustomUnit("Bag", BaseUnit)
Bag.size_for(sugar, Kilo(0.250))
Bag.size_for(starch, Kilo(1.2))

Bottle = CustomUnit("Bottle", BaseUnit)
Bottle.size_for(rasp_flav, Litre("2.5"))
Bottle.size_for(apple_flav, Litre("2.8"))

Roll = CustomUnit("Roll", BaseUnit)
Roll.size_for(wrapper, Sq_Metre(10))

# Our product
prod_1 = ContinuousProduct("Raspberry Sweet", BaseUnit)

prod_1.add_component(sugar, qty=Kilo("7.2"), per=Unit(1000))
prod_1.add_component(starch, qty=Gram(2), per=Unit(1))
prod_1.add_component(rasp_flav, qty=Bottle(1), per=Unit(20000))
prod_1.add_component(wrapper, qty=Sq_Centimetre(9), per=Unit(1))
for row in prod_1._consumables:
    print(row)

print("###########")

prod_2 = ContinuousProduct("Apple Sweet", BaseUnit)

prod_2.add_component(sugar, qty=Kilo("7.2"), per=Unit(1000))
prod_2.add_component(starch, qty=Gram(2), per=Unit(1))
prod_2.add_component(apple_flav, qty=Bottle(1), per=Unit(15000))
prod_2.add_component(wrapper, qty=Sq_Centimetre(9), per=Unit(1))

party_mix = ContinuousProduct("Party Mix", BaseUnit)
party_mix.add_component(prod_1, qty=Unit(5), per=Unit(1))
party_mix.add_component(prod_2, qty=Unit(5), per=Unit(1))
for row in party_mix._products:
    print(row)
print("###########")

# Try something that isn't made in Unit quantities
goopTM = ContinuousProduct("Goop (TM)", FluidVolume)
goopTM.add_component(sugar, qty=Kilo("0.5"), per=Litre(1))
goopTM.add_component(starch, qty=Kilo(20), per=Litre(250))
goopTM.add_component(rasp_flav, qty=Millilitre(19), per=Litre(2))
for row in goopTM._consumables:
    print(row)
