from app.modules import OrderManager, OrderError
from app.modules import CakeProduceManager, DeliveryManager
from app.modules import ExternalProducerSupervisor
from app.modules import response_builder, validate_http_request, parse_kinesis_payload, configure_logging
from app.models import EventOrderModel, EventFulfillOrderModel, EventDeliveredOrderModel

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
    detail, is_complete = order.fulfill_order(fulfillment_id=fulfillment_id)

    logger.info(detail)
    if not is_complete:
        return response_builder(404, {'detail': detail})

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


def notify_delivery_company(event, context):
    """Notifying third-parties delivery companies about order

    SQS Trigger
    """
    detail = 'We called the delivery! Really!!'
    logger.info(detail)


@validate_http_request(validation_model=EventDeliveredOrderModel)
def order_delivered(event, context):
    """

    HTTP Trigger
    """
    event = EventDeliveredOrderModel(**event).dict()
    order_id = event.get('body').get('order_id')
    order_review = event.get('body').get('order_review')
    delivery_company_id = event.get('body').get('delivery_company_id')

    dm = DeliveryManager()
    detail = dm.order_delivered(order_id, delivery_company_id, order_review)

    return response_builder(200, {'detail': detail})


def notify_customer_service(event, context):
    """Notifying customer service about delivery

    SQS Trigger
    """
    detail = 'We called the customer service endpoint! Really!!'
    logger.info(detail)

