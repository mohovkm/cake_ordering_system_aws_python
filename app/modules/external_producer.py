from abc import ABC, abstractmethod


class ExternalProducerException(Exception):
    pass


class ExternalProducer(ABC):
    event_type: str

    @abstractmethod
    def handle_orders(self, records: list):
        pass
