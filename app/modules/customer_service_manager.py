from boto3 import client
from os import getenv
import json


class DeliveryManagerException(Exception):
    pass


class EmptyParameterException(DeliveryManagerException):
    pass


class CustomerServiceManager:
    def __init__(self):
        """
        """
        region_name = getenv('REGION')
        if not region_name:
            detail = 'ENV variable "REGION" can\'t be empty'
            raise EmptyParameterException(detail)

        customer_service_queue = getenv('CUSTOMER_SERVICE_QUEUE')
        if not customer_service_queue:
            detail = 'ENV variable "CUSTOMER_SERVICE_QUEUE" can\'t be empty'
            raise EmptyParameterException(detail)

        self.region_name = region_name
        self.customer_service_queue = customer_service_queue

        self.sqs_client = client(
            'sqs',
            region_name=region_name
        )

    def notify_customer_service_for_review(self, order_id, order_review):
        """
        """
        review = {
            'order_id': order_id,
            'order_review': order_review
        }

        params = {
            'MessageBody': json.dumps(review),
            'QueueUrl': self.customer_service_queue
        }

        self.sqs_client.send_message(**params)

