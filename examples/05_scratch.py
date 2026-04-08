from pro_machina import (
    ContinuousMachine,
    ContinuousProduct,
    DemandForecast,
    Order,
    Problem,
    ShiftPattern,
)
from pro_machina.durations import Mins, Weeks
from pro_machina.measures import BaseUnit, CustomUnit, Unit

problem = Problem(start_time="2026-03-02 00:00:00", length=Weeks(1))

prod_a = ContinuousProduct("Something", BaseUnit)

Box = CustomUnit("Box", BaseUnit)
Box.size_for(prod_a, Unit(49))

mac = ContinuousMachine("test machine")
mac.add_shift(ShiftPattern.load_example_pattern("six_two_example"))

forecast = DemandForecast()
forecast.add_demand(Order(prod_a, "2026-03-06", qty=Box(200)))

mac.add_product(prod_a, Box("1.6"), per=Mins(1))

problem.set_forecast(forecast)
problem.add_machine(mac)

problem.build()
