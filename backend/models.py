from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime

from backend.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_name = Column(String)
    store_location = Column(String)

    lens_type = Column(String)
    lens_index = Column(String)
    coating = Column(String)
    frame = Column(String)

    left_power = Column(String)
    right_power = Column(String)

    status = Column(String)

    inventory_available = Column(Boolean)

    sla_days = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    # ADDED FIELDS FOR GAP 1 AND GAP 3
    parent_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    delay_reason = Column(String, nullable=True)

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    lens_type = Column(String)
    power = Column(String)

    quantity = Column(Integer)

    # ADDED FIELDS FOR GAP 6
    coating = Column(String, nullable=True)
    lens_index = Column(String, nullable=True)

class OrderHistory(Base):
    __tablename__ = "order_history"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer)

    status = Column(String)

    updated_at = Column(DateTime, default=datetime.utcnow)