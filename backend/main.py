from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from backend.database import engine, SessionLocal
from backend.models import Base
from backend.schemas import OrderCreate, StatusUpdate, InventoryUpdate
from backend.crud import (
    create_order,
    get_orders,
    update_order_status,
    get_dashboard_stats,
    get_inventory,
    update_inventory_status
)
from backend.ai_service import (
    predict_delay_risk,
    inventory_recommendation
)
from backend.priority_service import get_priority
from backend.sla_service import predict_sla_breach
from backend.ml_predictor import predict_delay
from backend.bottleneck_service import analyze_bottlenecks

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



@app.get("/")
def home():
    return {"message": "AI Order Management System"}


@app.post("/orders")
def add_order(order: OrderCreate):

    db: Session = SessionLocal()

    try:
        return create_order(db, order)

    finally:
        db.close()

@app.get("/orders")
def fetch_orders():

    db: Session = SessionLocal()

    try:
        return get_orders(db)

    finally:
        db.close()

@app.put("/orders/{order_id}/status")
def change_status(order_id: int, status_update: StatusUpdate):

    db: Session = SessionLocal()

    try:
        return update_order_status(
            db,
            order_id,
            status_update.status
        )

    finally:
        db.close()

@app.get("/dashboard")
def dashboard():

    db: Session = SessionLocal()

    try:
        return get_dashboard_stats(db)

    finally:
        db.close()

@app.get("/ai/predictions")
def get_predictions(
    db: Session = Depends(get_db)
):

    orders = get_orders(db)

    predictions = []

    for order in orders:

        risk = predict_delay(order)

        predictions.append({
            "order_id": order.id,
            "customer_name": order.customer_name,
            "status": order.status,
            "predicted_risk": risk
        })

    return predictions

@app.get("/ai/inventory-recommendations")
def get_inventory_recommendations(
    db: Session = Depends(get_db)
):

    inventory_items = get_inventory(db)

    return inventory_recommendation(
        inventory_items
    )

@app.get("/ai/priorities")
def get_priorities():

    db: Session = SessionLocal()

    try:

        orders = get_orders(db)

        priorities = []

        for order in orders:

            result = get_priority(order)

            priorities.append({
                "order_id": order.id,
                "customer_name": order.customer_name,
                "status": order.status,
                "priority": result["priority"],
                "reason": result["reason"]
            })

        return priorities

    finally:
        db.close()

@app.get("/ai/sla-predictions")
def get_sla_predictions():

    db: Session = SessionLocal()

    try:

        orders = get_orders(db)

        results = []

        for order in orders:

            prediction = predict_sla_breach(order)

            results.append({
                "order_id": order.id,
                "customer_name": order.customer_name,
                "status": order.status,
                "sla_days": order.sla_days,
                "sla_risk": prediction["sla_risk"],
                "message": prediction["message"]
            })

        return results

    finally:
        db.close()

@app.get("/ai/bottlenecks")
def get_bottlenecks():

    db: Session = SessionLocal()

    try:

        orders = get_orders(db)

        return analyze_bottlenecks(
            orders
        )

    finally:
        db.close()

@app.put("/orders/{order_id}/inventory")
def update_inventory(
    order_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db)
):

    order = update_inventory_status(
        db,
        order_id,
        inventory.inventory_available
    )

    if not order:
        return {
            "error": "Order not found"
        }

    return {
        "message": "Inventory updated",
        "order_id": order.id,
        "inventory_available": order.inventory_available
    }