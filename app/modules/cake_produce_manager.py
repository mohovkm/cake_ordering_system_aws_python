import boto3
from os import getenv
import json
from .external_producer import ExternalProducer, ExternalProducerException


class CakeProduceManagerException(ExternalProducerException):
    pass


class EmptyParameterException(CakeProduceManagerException):
    pass


class CakeProduceManager(ExternalProducer):
    event_type = 'order_placed'

    def __init__(self):
        """
        """
        region_name = getenv('REGION')
        if not region_name:
            detail = 'ENV variable "REGION" can\'t be empty'
            raise EmptyParameterException(detail)

        cake_producer_email = getenv('CAKE_PRODUCER_EMAIL')
        if not cake_producer_email:
            detail = 'ENV variable "CAKE_PRODUCER_EMAIL" can\'t be empty'
            raise EmptyParameterException(detail)

        ordering_system_email = getenv('ORDERING_SYSTEM_EMAIL')
        if not ordering_system_email:
            detail = 'ENV variable "ORDERING_SYSTEM_EMAIL" can\'t be empty'
            raise EmptyParameterException(detail)

        self.region_name = region_name
        self.cake_producer_email = cake_producer_email
        self.ordering_system_email = ordering_system_email

        self.email_client = boto3.client(
            'ses',
            region_name=region_name
        )

    def handle_orders(self, orders_placed: list):
        """Handling the order and notifying the cake producers
        """
        email_results = []

        for order in orders_placed:
            email_results.append(
                self.notify_cake_producers_by_email(order)
            )

        print(email_results)
        return email_results

    def notify_cake_producers_by_email(self, order):
        """Sending an Email to cake producer
        """
        params = {
            'Destination': {
                'ToAddresses': [self.cake_producer_email]
            },
            'Message': {
                'Body': {
                    'Text': {
                        'Data': json.dumps(order)
                    }
                },
                'Subject': {
                    'Data': 'New cake order'
                }
            },
            'Source': self.ordering_system_email
        }

        return self.email_client.send_email(**params)

