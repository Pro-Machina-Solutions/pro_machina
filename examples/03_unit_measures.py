from pro_machina import ContinuousProduct
from pro_machina.measures import CM, UNIT, CustomUnit, M

roll = CustomUnit("Roll", M)
box = CustomUnit("Box", UNIT)

prod_a = ContinuousProduct("Something", unit_measures=[roll, M])
prod_b = ContinuousProduct("Else", unit_measures=UNIT)
roll.size_for(item=prod_a, unit=CM(20))
box.size_for(prod_b, UNIT(12))
# a = UNIT
# print(a._unit)
# b = a(12)
# print(b._unit)
# a = UNIT(1)
# print(box._unit)
# print(a._unit)
# print(box._unit)
