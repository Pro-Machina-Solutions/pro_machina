from pro_machina import ContinuousProduct
from pro_machina.measures import CM, UNIT, CustomUnit, M, KG

roll = CustomUnit("Roll", M)
box = CustomUnit("Box", UNIT)

prod_a = ContinuousProduct("Something", unit_measures=[roll, M])
prod_b = ContinuousProduct("Else", unit_measures=UNIT)

roll.size_for(prod_a, KG(20))
box.size_for(prod_b, UNIT(12))

