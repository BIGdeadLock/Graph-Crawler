from abc import ABC, abstractmethod

from collections import namedtuple

CallbackResult = namedtuple('ParsedResult', ['domain', 'url', 'data', 'type'])


class GraphCallback(ABC):
    """
    Abstract class for callbacks. Callbacks are used to process the data in a way that does not relate to the
    scraping procedure. For example add the data to a database or a file, parse the data to extract more information,
     etc.
    """
    @abstractmethod
    def process(self, graph, data):
        pass

    @staticmethod
    @abstractmethod
    def get_id() -> str:
        pass
