def predict_sla_breach(order):

    if order.sla_days <= 1:

        return {
            "sla_risk": "BREACH_RISK",
            "message": "Order may miss SLA"
        }

    elif order.sla_days <= 3:

        return {
            "sla_risk": "MONITOR",
            "message": "Monitor closely"
        }

    return {
        "sla_risk": "SAFE",
        "message": "Within SLA"
    }