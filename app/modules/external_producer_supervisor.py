from .external_producer import ExternalProducer, ExternalProducerException
from typing import Type


class ExternalProducerSupervisor:
    @staticmethod
    def filter_orders(records: list, order_type: str):
        """
        """
        return [record for record in records if record.get('event_type', {}).get('S') == order_type]

    def handle(self, producer: Type[ExternalProducer], records: list) -> str:
        """
        """
        try:
            ex_producer = producer()
        except ExternalProducerException as e:
            detail = f'ERROR: [{str(e)}]'
            return detail

        records = self.filter_orders(records, ex_producer.event_type)

        if len(records) == 0:
            detail = 'There is no orders_placed'

            return detail

        ex_producer.handle_orders(records)

        detail = 'everything went well'

        return detail
