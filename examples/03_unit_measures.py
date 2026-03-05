from pro_machina import BatchProduct, ContinuousProduct
from pro_machina.measures import UNIT, M, UnitRegister

prod_a = ContinuousProduct("Something")
prod_b = ContinuousProduct("Else")
prod_c = BatchProduct("Test")

print(prod_a._id)
print(prod_b._id)
print(prod_c._id)

reg = UnitRegister()
reg.add("roll", prod_a, M(10))
reg.add("roll", prod_b, M(20))
reg.add("box", prod_c, UNIT(50))

reg2 = UnitRegister()
print(reg2.prod_units)
