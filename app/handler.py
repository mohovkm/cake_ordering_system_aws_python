from app.modules import OrderManager, OrderError
from app.modules import CakeProduceManager, CakeError
from app.modules import response_builder, validate_http_request, parse_kinesis_payload
from app.models import EventOrderModel, EventFulfillOrderModel


@validate_http_request(validation_model=EventOrderModel)
def create_order(event, context):
    """Creating an order from HTTP request
    """
    event = EventOrderModel(**event).dict()

    # Creating and order object
    try:
        order = OrderManager()
    except OrderError as e:
        detail = {
            'detail': str(e)
        }
        return response_builder(400, detail)

    order.create_new_order(event.get('body'))
    # Saving order into DynamoDB and Kinesis
    saved_order = order.place_new_order()

    return response_builder(200, saved_order)


@validate_http_request(validation_model=EventFulfillOrderModel)
def fulfill_order(event, context):
    """Fulfilling order with extra parameters
    """
    event = EventFulfillOrderModel(**event).dict()
    order_id = event.get('body').get('order_id')
    fulfillment_id = event.get('body').get('fulfillment_id')

    # Creating and order object
    try:
        order = OrderManager(order_id=order_id)
    except OrderError as e:
        detail = {
            'detail': str(e)
        }
        return response_builder(400, detail)

    # Fulfilling order
    order.fulfill_order(fulfillment_id=fulfillment_id)

    detail = {
        'detail':  f'Order with order_id: {order_id} was sent to delivery'
    }
    return response_builder(200, detail)


def notify_cake_producer(event, context):
    """
    """
    # Receiving orders from an event
    records = [parse_kinesis_payload(record) for record in event.get('Records', [])]

    # Filtering orders to get only placed orders
    orders_placed = [record for record in records if record.get('event_type', {}).get('S') == 'order_placed']

    if len(orders_placed) == 0:
        print('There is no orders_placed')
        return 'notify_cake_producer: nothing to do'

    try:
        cake_producer = CakeProduceManager()
    except CakeError as e:
        detail = f'There is an error: {str(e)}'
        print(detail)
        return detail

    # Notifying producers
    cake_producer.handle_placed_orders(orders_placed)

    return 'notify_cake_producer: everything went well'
