"""
Constraints (both hard and soft) are broadly categorised into six levels.
These are, from the most granular to the most broad:
1. Default "constraints" (set by Config) that are somewhat pseudo-constraints
2. Product-level constraints
3. Product-group-level constraints
4. Machine-level constraints
5. Machine-group-level
6. Problem-level constraints

The hierarchy of constraints proceeds in that order, too. So, a machine-level
constraint will supercede any product-level constraint, and a problem-level
constraint will override any machine- or product-level constraint.

In this example, we'll start with the product-level constraint and the
additional example files will show how this hierarchy hopefully builds into a
coherent statement of the overall constraints within the problem.
"""

from pro_machina import ContinuousMachine, ContinuousProduct, Problem
from pro_machina.config import Config
from pro_machina.durations import Hours, Mins, Weeks
from pro_machina.measures import BaseUnit, Unit
from pro_machina.problem.constraints import (
    MaxProductionTime,
    MinProductionTime,
)

a = MinProductionTime
b = MaxProductionTime

# The first thing to do is create an example product
product_1 = ContinuousProduct(name="Product 1", base_dimension=BaseUnit)

# Before touching the constraint modules themselves, we need to look at the
# Config option which sets one default constraint, and another as a guide for
# the solver.

# The Pro Machina solver works by swapping blocks of production between
# different products or downtime and evaluates the cost function of the new
# solution. For Continuous problems, we need to have sensible bounds on the
# the duration of these blocks. If we set a lower bound of 15 minutes then we
# might get a solution where machines sometimes swich rapidly between different
# products in a way that is utterly nonsensical. Equally, we don't want the
# solver trying to consider whether dumping an entire 48 hour block of
# production into a schedule is a good/bad move in one single iteration.

# The defaults are a lower bound of 4 hours and an upper bound of 12 hours. If
# you wanted to change them (we don't here) then you can do so as follows:
config = Config()
config.min_default_swap_block = Hours(4)
config.max_default_swap_block = Hours(12)

# Pass the new config to the problem to override the defaults
problem = Problem(
    start_time="2026-03-02 00:00:00", length=Weeks(1), config=config
)

# It's important to know what this means. Two things:

# 1 - No run of a product will be for less than 4 hours (unless we use a
#     constraint coming up) or unless it isn't a factor of the shift duration.
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
product_1.add_hard_constraint(MaxProductionTime(value=Hours(24)))

# Now we can create two machines and add this product to each of them
machine_1 = ContinuousMachine("Machine 1")
machine_2 = ContinuousMachine("Machine 2")

machine_1.add_product(product_1, run_rate=Unit(50), per=Mins(1))
machine_2.add_product(product_1, run_rate=Unit(60), per=Mins(1))

# Internally, we can see that the hard constraint of the product has been
# propagated over to both machines. Don't worry about the syntax here as we're
# looking at the internals just to demonstrate; this isn't part of the API.
print()
print("Machine 1 constraints")
print(machine_1._products[0]["hard_constraints"], "\n")
print("Machine 2 constraints")
print(machine_2._products[0]["hard_constraints"])
print("********************\n")

# You might notice that the Start date and End date fields are None - that's
# because, without specifying them in the constraint itself, they are assumed
# to hold throughout the entire problem duration. You can set time boundaries
# to change the settings for different periods and add the constraint multiple
# times to a single product.
# NOTE: you are responsible for ensuring that you define the constraints to
# cover a contiguous block of dates across the problem duration.
