from pydantic import BaseModel, Json


class FulfillOrderModel(BaseModel):
    order_id: str
    fulfillment_id: str


class EventFulfillOrderModel(BaseModel):
    body: Json[FulfillOrderModel]
