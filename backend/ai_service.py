def predict_delay_risk(order):

    # Delivered orders are safe
    if order.status == "DELIVERED":

        return {
            "risk": "LOW",
            "reason": "Order already delivered"
        }

    # Orders currently in production
    elif order.status == "LENS_CUTTING":

        return {
            "risk": "LOW",
            "reason": "Order is in production"
        }

    # SLA about to expire
    elif order.sla_days <= 1:

        return {
            "risk": "HIGH",
            "reason": "SLA deadline approaching"
        }

    # Inventory unavailable
    elif not order.inventory_available:

        return {
            "risk": "HIGH",
            "reason": "Required inventory unavailable"
        }

    # Normal monitoring
    else:

        return {
            "risk": "MEDIUM",
            "reason": "Order should be monitored"
        }
    
def inventory_recommendation(inventory_items):

    recommendations = []

    for item in inventory_items:

        if item.quantity <= 5:

            recommendations.append({
                "lens_type": item.lens_type,
                "power": item.power,
                "current_stock": item.quantity,
                "recommendation": "Reorder Soon"
            })

    return recommendations