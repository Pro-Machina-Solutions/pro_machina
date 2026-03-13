"""
This example will follow almost the exact setup of the last example but will
demonstrate a bit more complexity by discussing starting stocks and inbound
deliveries of consumables. In addition, we don't just have to have concrete
orders driving demand - we can additionally have MadeToStock targets
"""

from itertools import count
from random import randint

from pro_machina import (
    Config,
    Consumable,
    ContinuousMachine,
    ContinuousProduct,
    DemandForecast,
    InboundStock,
    MadeToStock,
    Order,
    Problem,
    ShiftPattern,
    StockHolding,
)
from pro_machina.durations import Mins, Weeks
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
    Tonne,
    Unit,
    Weight,
)

config = Config()
# We'll solve for a longer time period
problem = Problem(
    start_time="2026-03-02 00:00:00", length=Weeks(4), config=config
)

# For Consumables, this time we will leave them as rate-limiting (the default).
# Note that we are specifying some metadata for our own (made up) product code
# and a unit that we want to measure stock in
counter = count(500)
sugar = Consumable(
    "Sugar", Weight, meta={"code": f"A{next(counter)}", "stock_measure": Tonne}
)
gelatine = Consumable(
    name="Gelatine",
    base_dimension=Weight,
    meta={"code": f"A{next(counter)}", "stock_measure": Kilo},
)
rasp_flav = Consumable(
    "Raspberry Flavour",
    FluidVolume,
    meta={"code": f"A{next(counter)}", "stock_measure": Litre},
)
apple_flav = Consumable(
    "Apple Flavour",
    FluidVolume,
    meta={"code": f"A{next(counter)}", "stock_measure": Litre},
)
straw_flav = Consumable(
    "Strawberry Flavour",
    FluidVolume,
    meta={"code": f"A{next(counter)}", "stock_measure": Litre},
)
red_wrap = Consumable(
    "Red Wrapper",
    Area,
    meta={"code": f"A{next(counter)}", "stock_measure": Sq_Metre},
)
green_wrap = Consumable(
    "Green Wrapper",
    Area,
    meta={"code": f"A{next(counter)}", "stock_measure": Sq_Metre},
)
pink_wrap = Consumable(
    "Pink Wrapper",
    Area,
    meta={"code": f"A{next(counter)}", "stock_measure": Sq_Metre},
)

# Now we will define some starting stock levels. If no stock level is defined
# then it will be assumed to be 0 and no products containing that item will be
# made (unless they are not rate-limiting). The manual way to do this is:
stock = StockHolding(item=sugar, qty=Tonne(45))
problem.add_stock(stock)

# However, if we have a lot of consumables, we might have a lookup table of
# stock levels available already. Instead, we can iterate through all existing
# consumables that have been defined but ignoring Sugar since we covered that.
all_consumables = Consumable.get_all()
for con in all_consumables:
    if con.name == "Sugar":
        continue

    fake_level = randint(5, 20)
    holding = StockHolding(con, con.meta["stock_measure"](fake_level))
    problem.add_stock(holding)

    print(
        "Added",
        con.meta["stock_measure"](fake_level),
        "of stock to",
        con.name,
        f"({con.meta['code']})",
    )

# One other thing is that we might have deliveries inbound for some consumables
# that we want to take into account. This could be helpful with rate-limiting
# consumables where a stockout will introduce a natural production constraint
# until the replenishment is received
problem.add_inbound_stock(
    InboundStock(item=sugar, qty=Tonne(20), date="2026-03-02 00:00:00")
)

product_1 = ContinuousProduct(name="Raspberry Sweet", base_dimension=BaseUnit)
product_2 = ContinuousProduct(name="Apple Sweet", base_dimension=BaseUnit)
product_3 = ContinuousProduct(name="Strawberry Sweet", base_dimension=BaseUnit)

product_1.add_component(sugar, qty=Gram(7.2), per=Unit(1))
product_1.add_component(gelatine, qty=Gram(0.5), per=Unit(1))
product_1.add_component(rasp_flav, qty=Millilitre(0.2), per=Unit(1))
product_1.add_component(pink_wrap, Sq_Centimetre(10), per=Unit(1))

product_2.add_component(sugar, qty=Kilo(7.3), per=Unit(1000))
product_2.add_component(gelatine, qty=Kilo(0.45), per=Unit(1000))
product_2.add_component(apple_flav, qty=Litre(0.2), per=Unit(1000))
product_2.add_component(green_wrap, qty=Sq_Metre(10), per=Unit(9800))

Bottle = CustomUnit("Bottle", dimension=FluidVolume)
Bottle.size_for(straw_flav, Fl_Ounce(12))

product_3.add_component(sugar, qty=Kilo("7.3"), per=Unit(1000))
product_3.add_component(gelatine, qty=Kilo("0.45"), per=Unit(1000))
product_3.add_component(straw_flav, qty=Bottle(2), per=Unit(10000))
product_3.add_component(red_wrap, qty=Sq_Metre(10), per=Unit(9800))

machine = ContinuousMachine(name="Machine A")
machine.add_product(product_1, run_rate=Unit(80), per=Mins(1))
machine.add_product(product_2, run_rate=Unit(75), per=Mins(1))
machine.add_product(product_3, run_rate=Unit(72), per=Mins(1))

shift = ShiftPattern.load_example_pattern("six_two_example")
machine.add_shift(shift)

problem.add_machine(machine)

party_mix = ContinuousProduct("Party Mix", base_dimension=BaseUnit)
party_mix.add_component(product_1, qty=Unit(8), per=Unit(1))
party_mix.add_component(product_2, qty=Unit(7), per=Unit(1))
party_mix.add_component(product_3, qty=Unit(9), per=Unit(1))

tub = Consumable("Party Mix Tub", BaseUnit, rate_limiting=False)
party_mix.add_component(tub, Unit(1), Unit(1))

machine_2 = ContinuousMachine("Bagging Machine")
machine_2.add_product(party_mix, run_rate=Unit(10), per=Mins(1))
problem.add_machine(machine_2)

forecast = DemandForecast()
forecast.add_order(Order(party_mix, date="2026-03-06", qty=Unit(1000)))

# In addition to the defined order, we can also set a steady demand to make to
# stock. This could be important for balancing production during quiet periods
# because pro_machina will let machines go idle if there is insufficient
# demand to jusify production. That can be managed more effectively with
# custom constraints that will be covered later, but for now we'll just set a
# custom demand level

# Here we specify a start date of the Friday following our set Order. This
# means that we will try shift the order first and then the following week the
# demand will switch to MTS. We set no end_date and set a freq of 1 week
# meaning that the MTS demand will be renewewed every week until the problem
# end date

# NOTE: It's not strictly true that the machine will switch priorities in such
# a strict manner (strictly handling orders and only then handliung MTS). In
# reality it's a lot more complicated and would be directed by other
# constraints (coming later) but it's helpful to conceptualise it this way
mts = MadeToStock(
    product=party_mix, start_date="2026-03-13", qty=Unit(800), freq=Weeks(1)
)

problem.set_forecast(forecast)

# If we want to set the stock levels for products, there is currently no
# aggregate method (e.g. `ContinuousProducts.get_all()`) because there are so
# many ways that they can be altered/used, so you may wish to aggregate them in
# your own structure
problem.build()
