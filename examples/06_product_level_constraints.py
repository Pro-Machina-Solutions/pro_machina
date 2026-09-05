"""
In this example, we'll start with the product-level constraint and the
additional example files will show how this hierarchy hopefully builds into a
coherent statement of the overall constraints within the problem.
"""

import pro_machina
from pro_machina import (
    ContinuousMachine,
    ContinuousProduct,
    DemandForecast,
    Problem,
)
from pro_machina.config import Config
from pro_machina.durations import Hours, Mins, Weeks
from pro_machina.measures import BaseUnit, Unit
from pro_machina.problem.constraints import (
    MinProductionTime,
    SeasonalProduction,
)

pro_machina.options["silence_warnings"] = True

# The first thing to do is create some example products.
product_1 = ContinuousProduct(name="Product 1", base_dimension=BaseUnit)
product_2 = ContinuousProduct(name="Product 2", base_dimension=BaseUnit)
product_3 = ContinuousProduct(name="Product 3", base_dimension=BaseUnit)
product_4 = ContinuousProduct(name="Product 4", base_dimension=BaseUnit)
product_5 = ContinuousProduct(name="Product 5", base_dimension=BaseUnit)
product_6 = ContinuousProduct(name="Product 6", base_dimension=BaseUnit)
product_7 = ContinuousProduct(name="Product 7", base_dimension=BaseUnit)
product_8 = ContinuousProduct(name="Product 8", base_dimension=BaseUnit)
product_9 = ContinuousProduct(name="Product 9", base_dimension=BaseUnit)
product_10 = ContinuousProduct(name="Product 10", base_dimension=BaseUnit)

# The Pro Machina solver works by swapping blocks of production between
# different products or downtime and evaluates the cost function of the new
# solution. For Continuous problems, we need to have sensible bounds on the
# the duration of these blocks. If we set a lower bound of 15 minutes then we
# might get a solution where machines sometimes swich rapidly between different
# products in a way that is utterly nonsensical. Equally, we don't want the
# solver trying to consider whether dumping an entire 48 hour block of
# production into a schedule is a good/bad move in one single iteration.

# The defaults are a lower bound of 4 hours and an upper bound of 12 hours. If
# you wanted to change them (we don't here, we're just resetting as the
# defaults) then you can do so as follows:
config = Config()
config.min_default_swap_block = Hours(4)
config.max_default_swap_block = Hours(12)

# Pass the new config to the problem to override the defaults
problem = Problem(
    start_time="2026-03-02 00:00:00", length=Weeks(1), config=config
)

# It's important to know what this means. Two things:

# 1 - No run of a product will be for less than 4 hours (unless we use a
#     constraint - coming up) or unless it isn't a factor of the shift
#     duration.
#     So, for example, it may be that a six hour shift will have four hours of
#     Product A and two hours of Product B, simply because the four hour block
#     of Product B happens to run into downtime.

# 2 - This does NOT mean that production runs of a single product for an entire
#     week are not possible. It only means that only a maximum of 12 hours of
#     production will be changed at any one time. It doesn't stop multiple such
#     blocks being stacked together in contiguous runs. We can limit production
#     runs using a hard constraint if needed.

# So, let's say that we're happy for production runs of no less than 4 hours
# for all products by default, but we want to change it for one product:
product_1.add_hard_constraint(MinProductionTime(value=Hours(2)))

# Now let's say that we also don't want unbounded runs on a single product. We
# already know that the maximum product swap under consideration is 12 hours,
# but what if we wanted to limit the number of contiguous blocks of a single
# product run? This will ensure that, at most, no more than 24 hours of
# consecutive production of our product can be done before either switching to
# another product or going offline.
# product_1.add_hard_constraint(MaxProductionTime(value=Hours(24)))

# Now we can create two machines and add this product to each of them
machine_1 = ContinuousMachine("Machine 1")
machine_2 = ContinuousMachine("Machine 2")

product_1.add_hard_constraint(
    SeasonalProduction(
        start_date="2026-03-05",
        end_date="2026-03-06",
    )
)

machine_1.add_product(product_1, run_rate=Unit(50), per=Mins(1))
machine_1.add_product(product_2, run_rate=Unit(50), per=Mins(1))
machine_2.add_product(product_1, run_rate=Unit(60), per=Mins(1))
machine_2.add_product(product_2, run_rate=Unit(50), per=Mins(1))
machine_2.add_hard_constraint(
    MinProductionTime(
        value=Hours(1), start_date="2026-03-03", end_date="2026-03-04"
    )
)
# print(machine_2._hard_constraints)
problem.add_machine(machine_1)
problem.add_machine(machine_2)
problem.set_forecast(DemandForecast())

problem.build()

# You might notice that the Start date and End date fields are None - that's
# because, without specifying them in the constraint itself, they are assumed
# to hold throughout the entire problem duration. You can set time boundaries
# to change the settings for different periods and add the constraint multiple
# times to a single product.
# NOTE: you are responsible for ensuring that you define the constraints to
# cover a contiguous block of dates across the problem duration.
