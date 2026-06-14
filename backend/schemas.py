from pydantic import BaseModel


class OrderCreate(BaseModel):
    customer_name: str
    store_location: str

    lens_type: str
    lens_index: str
    coating: str
    frame: str

    left_power: str
    right_power: str

    sla_days: int


class StatusUpdate(BaseModel):
    status: str

class InventoryUpdate(BaseModel):
    inventory_available: bool