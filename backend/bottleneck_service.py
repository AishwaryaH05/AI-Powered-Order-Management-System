def analyze_bottlenecks(orders):

    total_orders = len(orders)

    if total_orders == 0:
        return {
            "message": "No orders available"
        }

    status_count = {}

    for order in orders:

        status = order.status

        if status not in status_count:
            status_count[status] = 0

        status_count[status] += 1

    bottleneck_status = max(
        status_count,
        key=status_count.get
    )

    bottleneck_orders = status_count[
        bottleneck_status
    ]

    percentage = round(
        (bottleneck_orders / total_orders) * 100,
        2
    )

    recommendation = ""

    if bottleneck_status == "ORDER_PLACED":
        recommendation = (
            "Prioritize order processing and inventory allocation."
        )

    elif bottleneck_status == "LENS_CUTTING":
        recommendation = (
            "Increase production capacity."
        )

    else:
        recommendation = (
            "Monitor workflow."
        )

    return {
        "bottleneck_stage": bottleneck_status,
        "orders": bottleneck_orders,
        "percentage": percentage,
        "message":
            f"{percentage}% orders are currently in {bottleneck_status}",
        "recommendation": recommendation
    }