from backend.models import Order, Inventory, OrderHistory


def verify_and_deduct_stock(db, order_data) -> bool:
    if order_data.left_power == order_data.right_power:
        record = db.query(Inventory).filter(
            Inventory.lens_type == order_data.lens_type,
            Inventory.coating == order_data.coating,
            Inventory.lens_index == order_data.lens_index,
            Inventory.power == order_data.left_power
        ).first()
        if record and record.quantity >= 2:
            record.quantity -= 2
            return True
        return False
    else:
        left_record = db.query(Inventory).filter(
            Inventory.lens_type == order_data.lens_type,
            Inventory.coating == order_data.coating,
            Inventory.lens_index == order_data.lens_index,
            Inventory.power == order_data.left_power
        ).first()
        right_record = db.query(Inventory).filter(
            Inventory.lens_type == order_data.lens_type,
            Inventory.coating == order_data.coating,
            Inventory.lens_index == order_data.lens_index,
            Inventory.power == order_data.right_power
        ).first()
        if left_record and left_record.quantity >= 1 and right_record and right_record.quantity >= 1:
            left_record.quantity -= 1
            right_record.quantity -= 1
            return True
        return False


def create_order(db, order_data):

    inventory_available = verify_and_deduct_stock(db, order_data)

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


def get_orders(db, status: str = None, lens_type: str = None, store_location: str = None):
    query = db.query(Order)
    if status and status != "All":
        query = query.filter(Order.status == status)
    if lens_type and lens_type != "All":
        query = query.filter(Order.lens_type == lens_type)
    if store_location and store_location != "All":
        query = query.filter(Order.store_location == store_location)
    return query.all()

def update_order_status(db, order_id, new_status, delay_reason=None):

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        return None

    order.status = new_status
    if delay_reason is not None:
        order.delay_reason = delay_reason

    history = OrderHistory(
        order_id=order.id,
        status=new_status
    )

    db.add(history)

    # Spawn child order automatically if status is QC_FAILED
    if new_status == "QC_FAILED":
        inventory_available = verify_and_deduct_stock(db, order)

        child_order = Order(
            customer_name=order.customer_name,
            store_location=order.store_location,
            lens_type=order.lens_type,
            lens_index=order.lens_index,
            coating=order.coating,
            frame=order.frame,
            left_power=order.left_power,
            right_power=order.right_power,
            sla_days=order.sla_days,
            status="ORDER_PLACED",
            inventory_available=inventory_available,
            parent_order_id=order.id
        )
        db.add(child_order)

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