from backend.models import Order, Inventory, OrderHistory


def create_order(db, order_data):

    inventory_record = db.query(Inventory).filter(
        Inventory.lens_type == order_data.lens_type,
        Inventory.power == order_data.left_power
    ).first()

    inventory_available = inventory_record is not None

    new_order = Order(
        customer_name=order_data.customer_name,
        store_location=order_data.store_location,
        lens_type=order_data.lens_type,
        lens_index=order_data.lens_index,
        coating=order_data.coating,
        frame=order_data.frame,
        left_power=order_data.left_power,
        right_power=order_data.right_power,
        sla_days=order_data.sla_days,
        status="ORDER_PLACED",
        inventory_available=inventory_available
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


def get_orders(db):
    return db.query(Order).all()

def update_order_status(db, order_id, new_status):

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        return None

    order.status = new_status

    history = OrderHistory(
        order_id=order.id,
        status=new_status
    )

    db.add(history)

    db.commit()
    db.refresh(order)

    return order

def get_dashboard_stats(db):

    total_orders = db.query(Order).count()

    active_orders = db.query(Order).filter(
        Order.status != "DELIVERED"
    ).count()

    delivered_orders = db.query(Order).filter(
        Order.status == "DELIVERED"
    ).count()

    inventory_available_orders = db.query(Order).filter(
        Order.inventory_available == True
    ).count()

    return {
        "total_orders": total_orders,
        "active_orders": active_orders,
        "delivered_orders": delivered_orders,
        "inventory_available_orders": inventory_available_orders
    }

def get_inventory(db):
    return db.query(Inventory).all()

def update_inventory_status(
    db,
    order_id: int,
    inventory_available: bool
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        return None

    order.inventory_available = inventory_available

    db.commit()
    db.refresh(order)

    return order