from sqlalchemy import Column, Integer, String, Boolean, DateTime
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

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    lens_type = Column(String)
    power = Column(String)

    quantity = Column(Integer)

class OrderHistory(Base):
    __tablename__ = "order_history"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer)

    status = Column(String)

    updated_at = Column(DateTime, default=datetime.utcnow)