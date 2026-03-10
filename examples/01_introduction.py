"""
This module is designed to give a brief overview of the core objects in the
pro_machina library. In this example, we will be defining a very simple problem
and in subsequent examples we will continue to build on these foundations by
adding more features and defining more complexity.

Each example will assume knowledge from previous examples and only explain any
new features ebing introduced.
"""

from pro_machina import (
    Config,
    ContinuousMachine,
    ContinuousProduct,
    Problem,
    ShiftPattern,
)
from pro_machina.durations import Mins
from pro_machina.measures import BaseUnit, Unit

# The main object in the pro_machina library is the Problem. This serves as a
# container to define all of the characteristics of what you want to solve for.
# In complex setups, it's likely that a single instance will be passed around
# multiple modules as you build up the component parts.

# All problems require a reference start date, and take an optional Config
# instance. It is also possible that this config object will be passed around
# with the Problem in cases where you wish to change things like hiding
# warnings for specific modules. We'll just pass the defaults for now.
config = Config()
problem = Problem(start_time="2026-02-23 00:00:00", config=config)

# The next thing to do is to define some products that we want to make.
# Products are split into two categories: ContinuousProducts and BatchProducts.
# BatchProducts are typically what are used in a Job Shop Scheduling problem
# where a fixed quantity is produced within a fixed duration. However, we want
# to solve for producing ContinuousProducts here, which represent products
# that are manufactured in variable-length production runs at a fixed rate.
# Here we are going to product sweets and we'll case them in terms of
# individual units (the generic type for this is BaseUnit)
product_1 = ContinuousProduct(name="Raspberry Sweet", base_dimension=BaseUnit)
product_2 = ContinuousProduct(name="Apple Sweet", base_dimension=BaseUnit)
product_3 = ContinuousProduct(name="Strawberry Sweet", base_dimension=BaseUnit)

# Next we can define a machine. Like products, these are also split into two
# categories: BatchMachine and ContinuousMachine. We will need a
# ContinuousMachine to make our products and when we add them to the machine,
# we will define the production rate of each product
machine = ContinuousMachine(name="Machine A")

# The machine can make 80 Raspberry Sweets per minute, etc.
machine.add_product(product_1, run_rate=Unit(80), per=Mins(1))
machine.add_product(product_2, run_rate=Unit(75), per=Mins(1))
machine.add_product(product_3, run_rate=Unit(72), per=Mins(1))

# Next we need to specify a shift pattern for our machine. Defining shift
# patterns is an involved process that will be covered later. For now we'll
# load a pre-made example where the machine will run from 6am to 2pm, Monday to
# Friday with no breaks (though it will finish at 13:30 on Friday).
shift = ShiftPattern.load_example_pattern("six_two_example")
machine.add_shift(shift)

# Now our machine is fully specified, so we can add it to the Problem.
problem.add_machine(machine)

# TODO need to add a forecast

# Since we have nothing more to define, we can finalise the problem, ready to
# solve. A Problem can only be built once.
# TODO does nothing yet
problem.build()

# TODO does nothing yet
problem.solve()
