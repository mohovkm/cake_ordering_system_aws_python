from app.modules import OrderManager, OrderError
from app.modules import CakeProduceManager, DeliveryManager
from app.modules import ExternalProducerSupervisor
from app.modules import response_builder, validate_http_request, parse_kinesis_payload, configure_logging
from app.models import EventOrderModel, EventFulfillOrderModel

# Configuring logging for application. It's configured to standard stdout,
# because all stdout messages will go to the Amazon CloudWatch.
logger = configure_logging()


@validate_http_request(validation_model=EventOrderModel)
def create_order(event, context):
    """Creating an new order into the DynamoDB and Kinesis Stream.

    HTTP trigger.
    """
    event = EventOrderModel(**event).dict()

    # Creating and order object
    try:
        order = OrderManager()
    except OrderError as e:
        detail = str(e)
        logger.error(detail)

        return response_builder(400,  {'detail': detail})

    # Creating new order
    order.create_new_order(event.get('body'))

    # Saving order into DynamoDB and Kinesis
    saved_order = order.place_new_order()

    detail = f'Order with ID [{order.order_id}] created successfully'
    logger.info(detail)

    return response_builder(200, saved_order)


@validate_http_request(validation_model=EventFulfillOrderModel)
def fulfill_order(event, context):
    """Fulfilling existing order with extra parameters.

    HTTP trigger.
    """
    event = EventFulfillOrderModel(**event).dict()
    order_id = event.get('body').get('order_id')
    fulfillment_id = event.get('body').get('fulfillment_id')

    # Creating and order object
    try:
        order = OrderManager(order_id=order_id)
    except OrderError as e:
        detail = str(e)
        logger.error(detail)

        return response_builder(400, {'detail': detail})

    # Fulfilling order
    order.fulfill_order(fulfillment_id=fulfillment_id)

    detail = f'Order with order_id: {order_id} was sent to delivery'
    logger.info(detail)

    return response_builder(200, {'detail': detail})


def notify_external_parties(event, context):
    """Notifying External parties about orders conditions.

    Kinesis Stream trigger.
    """
    # Receiving orders from an event
    records = [parse_kinesis_payload(record) for record in event.get('Records', [])]

    # Creating a supervisor instance
    sv = ExternalProducerSupervisor()

    details = []

    # handling CakeProducer notifications
    detail = sv.handle(CakeProduceManager, records)
    details.append(detail)

    # handling DeliveryManager notifications
    detail = sv.handle(DeliveryManager, records)
    details.append(detail)

    # Logging the information
    for detail in details:
        logger.info(detail)

    return '; '.join(details)
