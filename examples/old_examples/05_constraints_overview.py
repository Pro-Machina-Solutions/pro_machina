"""
This module is to outline the general approach taken to constraints defined by
the user. The individual categories will then be expanded upon in subsequent
example files.

Constraints (both hard and soft) are broadly categorised into six levels.
These are, from the most granular to the most broad:
1. Default "constraints" (set by Config) that are somewhat pseudo-constraints.
   examples include `min_default_swap_block` and `max_default_swap_block`
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
