from pydantic import BaseModel, Json


class EventDeliveredOrderModelBase(BaseModel):
    order_id: str
    delivery_company_id: str
    order_review: int


class EventDeliveredOrderModel(BaseModel):
    body: Json[EventDeliveredOrderModelBase]
