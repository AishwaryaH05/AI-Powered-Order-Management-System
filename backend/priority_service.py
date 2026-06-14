def get_priority(order):

    if not order.inventory_available:
        return {
            "priority": "HIGH",
            "reason": "Inventory unavailable"
        }

    elif order.status == "LENS_CUTTING":
        return {
            "priority": "MEDIUM",
            "reason": "Production in progress"
        }

    elif order.status == "DELIVERED":
        return {
            "priority": "LOW",
            "reason": "Completed order"
        }

    return {
        "priority": "LOW",
        "reason": "No action required"
    }