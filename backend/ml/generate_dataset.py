import pandas as pd
import random

data = []

for i in range(5000):

    inventory_available = random.choice([0, 1])

    sla_days = random.randint(1, 7)

    status = random.choice([
        "ORDER_PLACED",
        "LENS_CUTTING",
        "DELIVERED"
    ])

    if inventory_available == 0:
        risk = "HIGH"

    elif status == "LENS_CUTTING":
        risk = "MEDIUM"

    else:
        risk = "LOW"

    data.append([
        inventory_available,
        sla_days,
        status,
        risk
    ])

df = pd.DataFrame(
    data,
    columns=[
        "inventory_available",
        "sla_days",
        "status",
        "delay_risk"
    ]
)

df.to_csv(
    "backend/ml/orders_training.csv",
    index=False
)

print("Dataset generated successfully")