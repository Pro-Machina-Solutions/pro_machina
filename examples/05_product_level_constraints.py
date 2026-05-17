"""
Constraints (both hard and soft) are broadly categorised into three levels.
These are, from the most granular to the most broad:
1. Product-level constraints
2. Machine-level constraints
3. Problem-level constraints

The hierarchy of constraints proceeds in that order, too. So, a machine-level
constraint will supercede any product-level constraint, and a problem-level
constraint will override any machine- or product-level constraint.

In this example, we'll start with the problem-level constraint and the
additional example files will show how this hierarchy hopefully builds into a
coherent statement of the overall constraints within the problem.
"""

from pro_machina import ContinuousMachine, ContinuousProduct
from pro_machina.durations import Hours, Mins
from pro_machina.measures import BaseUnit, Unit
from pro_machina.problem.constraints import (
    MaxProductionTime,
    MinProductionTime,
    ProductGroup,
)

a = MinProductionTime
b = MaxProductionTime
c = ProductGroup

# The first thing to do is create an example product
product_1 = ContinuousProduct(name="Product 1", base_dimension=BaseUnit)

# Swapping machines between products often comes with downtime. Therefore, to
# prevent unnecessary swapping, we might want to state that each production run
# of this product must be bounded by a minimum run time i.e. once the machine
# is set up and, even if it is *feasible* that you could swap after 1 hour if
# targets come down to the wire, you just practically can't keep swapping. Set
# a minimum runtime on the product-level.
product_1.add_hard_constraint(MinProductionTime(min_time=Hours(4)))

# Equally, it may be that you don't want a single continuous run of this
# product to exceed some threshold. This aspect is NOT as intuitive as you
# might initially think. Unlike MinProductionTime, there are good business
# reasons why you might run a single product for any arbitrary time period
# (weeks, even) to meet demand.

# Instead what this does is tell that algorithm that, during any swap in the
# search for a solution, it should not insert a production run into the
# schedule that exceeds this duration for a product. We set a Max here of 12
# hours but there's nothing stopping it putting three 12 hour runs of the same
# product back-to-back such that the outcome is a 36 hour continuous run of the
# same product.

# TODO: Perhaps this needs to be pushed into Config to avoid confusion? It's
# more an optimiser setting than a constraint
product_1.add_hard_constraint(MaxProductionTime(max_time=Hours(12)))

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
