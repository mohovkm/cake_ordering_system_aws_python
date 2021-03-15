from .external_producer import ExternalProducer, ExternalProducerException


class DeliveryManagerException(ExternalProducerException):
    pass


class EmptyParameterException(DeliveryManagerException):
    pass


class DeliveryManager(ExternalProducer):
    event_type = 'order_fulfilled'

    def handle_orders(self, records: list):
        """Handling the fulfilled records
        """
        # Code for notifying delivery manager. I'll do it, when I'll have a time.
        detail = 'Delivery was canceled'
        return detail
