from pro_machina import (
    Consumable,
    ContinuousMachine,
    ContinuousProduct,
    Problem,
)
from pro_machina.durations import Hours, Mins, Weeks
from pro_machina.measures import (
    Area,
    BaseUnit,
    CustomUnit,
    FluidVolume,
    Gram,
    Kilo,
    Litre,
    Sq_Centimetre,
    Sq_Metre,
    Unit,
    Weight,
)
from pro_machina.problem.constraints import (
    MaxProductionTime,
    MinProductionTime,
)

problem = Problem(start_time="2026-03-09 00:00:00", length=Weeks(1))

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
prod_1.add_hard_constraint(MinProductionTime(Hours(2)))
prod_1.add_hard_constraint(MaxProductionTime(Hours(6)))

mach = ContinuousMachine("test machine")
mach.add_product(prod_1, Unit(50), per=Mins(1))
mach.add_product_constraint(prod_1, MinProductionTime(Hours(3)))
print(mach._products)
