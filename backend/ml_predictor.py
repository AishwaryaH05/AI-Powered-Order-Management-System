import joblib

model = joblib.load(
    "backend/ml/model.pkl"
)

status_encoder = joblib.load(
    "backend/ml/status_encoder.pkl"
)

risk_encoder = joblib.load(
    "backend/ml/risk_encoder.pkl"
)


def predict_delay(order):

    status_value = status_encoder.transform(
        [order.status]
    )[0]

    inventory_value = (
        1 if order.inventory_available
        else 0
    )

    prediction = model.predict(
        [[
            inventory_value,
            status_value,
            order.sla_days
        ]]
    )

    risk = risk_encoder.inverse_transform(
        prediction
    )[0]

    return risk