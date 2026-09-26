from pro_machina.costs import PriceBand, PurchaseCost
from pro_machina.measures import Tonne, Weight
from pro_machina.problem import Consumable

Sugar = Consumable(
    "Sugar",
    base_dimension=Weight,
    purchase_cost=[
        PurchaseCost(
            price_bands=[
                PriceBand(
                    min_order=Tonne(1),
                    max_order=Tonne(10),
                    order_increment=Tonne(1),
                    cost_per_increment=450.00,
                ),
                PriceBand(
                    min_order=Tonne(10),
                    max_order=Tonne(100),
                    order_increment=Tonne(10),
                    cost_per_increment=4400.00,
                ),
            ],
            supplier=None,
            lead_time=None,
        )
    ],
)
print(Sugar)
