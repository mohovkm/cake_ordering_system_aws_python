import uuid
from datetime import datetime
from boto3 import client
from os import getenv
import json


class OrderManagerException(Exception):
    pass


class EmptyParameterException(OrderManagerException):
    pass


class OrderManager:
    def __init__(self, order_id: str = None):
        """Initialisation of OrderManager class
        """
        order_table_name = getenv('DYNAMO_ORDER_TABLE_NAME')
        if not order_table_name:
            detail = 'ENV variable "DYNAMODB_TABLE_NAME" can\'t be empty'
            raise EmptyParameterException(detail)

        order_stream_name = getenv('KINESIS_ORDER_STREAM_NAME')
        if not order_stream_name:
            detail = 'ENV variable "KINESIS_STREAM_NAME" can\'t be empty'
            raise EmptyParameterException(detail)

        self.order_table_name = order_table_name
        self.order_stream_name = order_stream_name

        self.dynamo_client = client('dynamodb')
        self.kinesis_client = client('kinesis')

        self._order_id = order_id or str(uuid.uuid4())

    def create_new_order(self, body):
        """Creating a schema order from body
        """
        self.order = {
            'order_id': {
                'S': self._order_id
            },
            'name': {
                'S': body.get('name', ''),
            },
            'address': {
                'S': body.get('address', ''),
            },
            'product_id': {
                'S':  body.get('product_id', ''),
            },
            'quantity': {
                'N': str(body.get('quantity', '')),
            },
            'order_date': {
                'N': str(int(datetime.now().timestamp())),
            },
            'event_type': {
                'S': 'order_placed'
            }
        }

    def place_new_order(self):
        """Saving new order into DynamoDB table and Kinesis stream.
        """
        self.save_order_in_dynamo()
        self.place_order_into_stream()

        return self.order

    def save_order_in_dynamo(self):
        """Saving new order into DynamoDB table
        """
        params = {
            'TableName': self.order_table_name,
            'Item': self.order
        }

        return self.dynamo_client.put_item(**params)

    def place_order_into_stream(self):
        """Placing new order into Kinesis
        """
        params = {
            'Data': json.dumps(self.order),
            'PartitionKey': self._order_id,
            'StreamName': self.order_stream_name
        }

        return self.kinesis_client.put_record(**params)

    def fulfill_order(self, fulfillment_id: str):
        """Fulfill order and save to dynamodb
        """
        self.get_order_from_dynamodb()
        self.create_fulfilled_order(fulfillment_id)
        self.save_order_in_dynamo()
        self.place_order_into_stream()

        return self.order

    def get_order_from_dynamodb(self):
        """Getting order from DynamoDB by order_id
        """
        params = {
            'Key': {
                'order_id': {
                    'S': self._order_id
                }
            },
            'TableName': self.order_table_name
        }

        result = self.dynamo_client.get_item(**params)

        self.order = result.get('Item')

        return self.order

    def create_fulfilled_order(self, fulfillment_id: str):
        """
        """
        self.order['fulfillment_id'] = {
            'S': fulfillment_id
        }

        self.order['fulfillment_date'] = {
            'N': str(int(datetime.now().timestamp()))
        }

        self.order['event_type'] = {
            'S': 'order_fulfilled'
        }

    @property
    def order_id(self):
        return self._order_id
