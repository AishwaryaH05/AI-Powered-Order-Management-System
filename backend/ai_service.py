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
    groups = {}
    for item in inventory_items:
        coating = getattr(item, 'coating', None) or ""
        lens_index = getattr(item, 'lens_index', None) or ""
        key = (item.lens_type, coating, lens_index)
        if key not in groups:
            groups[key] = 0
        groups[key] += item.quantity

    recommendations = []
    for (lens_type, coating, lens_index), total_qty in groups.items():
        if total_qty <= 5:
            recommendations.append({
                "lens_type": lens_type,
                "coating": coating,
                "lens_index": lens_index,
                "current_stock": total_qty,
                "recommendation": "Reorder Soon"
            })
    return recommendations