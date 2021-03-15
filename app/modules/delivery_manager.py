from .external_producer import ExternalProducer, ExternalProducerException
from .customer_service_manager import CustomerServiceManager
from .order_manager import OrderManager
from boto3 import client
from os import getenv
from datetime import datetime
import json


class DeliveryManagerException(ExternalProducerException):
    pass


class EmptyParameterException(DeliveryManagerException):
    pass


class DeliveryManager(ExternalProducer):
    event_type = 'order_fulfilled'

    def __init__(self):
        """
        """
        region_name = getenv('REGION')
        if not region_name:
            detail = 'ENV variable "REGION" can\'t be empty'
            raise EmptyParameterException(detail)

        delivery_company_queue = getenv('DELIVERY_COMPANY_QUEUE')
        if not delivery_company_queue:
            detail = 'ENV variable "DELIVERY_COMPANY_QUEUE" can\'t be empty'
            raise EmptyParameterException(detail)

        self.region_name = region_name
        self.delivery_company_queue = delivery_company_queue

        self.sqs_client = client(
            'sqs',
            region_name=region_name
        )

    def handle_orders(self, records: list):
        """Handling the fulfilled records
        """
        notification_results = []

        for record in records:
            order = OrderManager(record.get('order_id', {}).get('S', ''))
            order.update_order_for_delivery()

            notification_result = self.notify_delivery_company(order.order)
            notification_results.append(notification_result)

    def notify_delivery_company(self, order: dict):
        """
        """
        params = {
            'MessageBody': json.dumps(order),
            'QueueUrl': self.delivery_company_queue
        }

        response = self.sqs_client.send_message(**params)

        return response

    def order_delivered(self, order_id, delivery_company_id, order_review):
        """
        """
        result = self.update_order_after_delivery(order_id, delivery_company_id)
        if not result:
            detail = f'Can\'t find order with id: [{order_id}]'
            return detail

        cm = CustomerServiceManager()
        cm.notify_customer_service_for_review(order_id, order_review)

        detail = f'Order with order_id [{order_id}] was delivered successfully by company with ' \
                 f'company_id: [{delivery_company_id}]'

        return detail

    def update_order_after_delivery(self, order_id, delivery_company_id):
        """
        """
        order = OrderManager(order_id)
        result = order.get_order_from_dynamodb()
        if not result:
            return False

        order.order['delivery_company_id'] = {
            'S': delivery_company_id
        }

        order.order['delivery_date'] = {
            'N': str(int(datetime.now().timestamp()))
        }

        order.save_order_in_dynamo()

        return order
