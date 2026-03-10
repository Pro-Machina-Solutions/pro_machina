"""
In the previous example, we gave a baseline definition of the products that we
want to make. But in reality, products have many specifications, consumables
involved in their production and can form layers moving through from WIP to a
finished product.

We'll expand the definition here, still usingm sweets but making multiple
levels of products
"""

from pro_machina import (
    Config,
    Consumable,
    ContinuousMachine,
    ContinuousProduct,
    Problem,
    ShiftPattern,
)
from pro_machina.durations import Mins
from pro_machina.measures import (
    Area,
    BaseUnit,
    CustomUnit,
    Fl_Ounce,
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
problem = Problem(start_time="2026-02-23 00:00:00", config=config)

# We'll define some consumables that will be used in our products. For now we
# just define their base dimensions and we'll specify quantities for individual
# products later
sugar = Consumable("Sugar", Weight)
gelatine = Consumable("Gelatine", Weight)
rasp_flav = Consumable("Raspberry Flavour", FluidVolume)
apple_flav = Consumable("Apple Flavour", FluidVolume)
straw_flav = Consumable("Strawberry Flavour", FluidVolume)
red_wrap = Consumable("Red Wrapper", Area)
green_wrap = Consumable("Green Wrapper", Area)
pink_wrap = Consumable("Pink Wrapper", Area)

# Making the same products as before
product_1 = ContinuousProduct(name="Raspberry Sweet", base_dimension=BaseUnit)
product_2 = ContinuousProduct(name="Apple Sweet", base_dimension=BaseUnit)
product_3 = ContinuousProduct(name="Strawberry Sweet", base_dimension=BaseUnit)

# Product 1 we will just define on a per-unit basis
product_1.add_component(sugar, qty=Gram(7.2), per=Unit(1))
product_1.add_component(gelatine, qty=Gram(0.5), per=Unit(1))
product_1.add_component(rasp_flav, qty=Millilitre(0.2), per=Unit(1))
product_1.add_component(pink_wrap, Sq_Centimetre(10), per=Unit(1))

# product_2 will use larger units, which will internally be converted into the
# base units similar to product_1, with some changes
product_2.add_component(sugar, qty=Kilo(7.3), per=Unit(1000))
product_2.add_component(gelatine, qty=Kilo(0.45), per=Unit(1000))
product_2.add_component(apple_flav, qty=Litre(0.2), per=Unit(1000))
product_2.add_component(green_wrap, Sq_Metre(10), per=Unit(9800))

# product_3 is going to be more complicated. In the case of the flavouring, we
# don't know how much goes into a single unit. All we know is that 2 bottles
# (purchased in Imperial units) is enough for 10,000 units. We can build this
# in two stages:
#   1 - First make a container called "Bottle". It doesn't have any fixed size
#       yet, it's just a conceptual container
#   2 - Size the bottle specifically for our flavouring

Bottle = CustomUnit("Bottle", dimension=FluidVolume)
Bottle.size_for(straw_flav, Fl_Ounce(12))

# Note that we could easily just size the Bottle for any other product.
# The specific size is stored for each individual consumable/product so it can
# be sized for any number of unique objects. We're not going to use these but
# e.g.
Bottle.size_for(apple_flav, Litre("1.5"))
Bottle.size_for(straw_flav, Millilitre(250))

# What we CANNOT do, though, is define is as something incompatible with its
# base unit:
# Bottle.size_for(apple_flav, Kilo("1.5")) This will fail

# Note also that I've also chosen to pass the float values as a string. This is
# because units are handled as type decimal.Decimal internally, so passing a
# string will help prevent floating-point error as the number of units scales
product_3.add_component(sugar, qty=Kilo("7.3"), per=Unit(1000))
product_3.add_component(gelatine, qty=Kilo("0.45"), per=Unit(1000))
product_3.add_component(straw_flav, qty=Bottle(2), per=Unit(10000))
product_3.add_component(green_wrap, Sq_Metre(10), per=Unit(9800))

machine = ContinuousMachine(name="Machine A")
machine.add_product(product_1, run_rate=Unit(80), per=Mins(1))
machine.add_product(product_2, run_rate=Unit(75), per=Mins(1))
machine.add_product(product_3, run_rate=Unit(72), per=Mins(1))

shift = ShiftPattern.load_example_pattern("six_two_example")
machine.add_shift(shift)

problem.add_machine(machine)

# Now that we have some individual sweets being made, we can also make a
# finished product containing them. We'll also need another machine somewhere
# else in the factory to create this product
party_mix = ContinuousProduct("Party Mix", base_dimension=BaseUnit)
party_mix.add_component(product_1, qty=Unit(8), per=Unit(1))
party_mix.add_component(product_2, qty=Unit(7), per=Unit(1))
party_mix.add_component(product_3, qty=Unit(9), per=Unit(1))

machine_2 = ContinuousMachine("Bagging Machine")
machine_2.add_product(party_mix, run_rate=Unit(10), per=Mins(1))

problem.add_machine(machine_2)

problem.build()

problem.solve()
