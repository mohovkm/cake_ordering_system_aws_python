from pydantic import BaseModel, Json


class CreateOrderModel(BaseModel):
    name: str
    address: str
    product_id: str
    quantity: int


class EventOrderModel(BaseModel):
    body: Json[CreateOrderModel]
