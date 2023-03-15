from abc import ABC, abstractmethod

from requests import Response


class Scraper(ABC):

    @abstractmethod
    def scrape(self, response: Response) -> list:
        pass

    @abstractmethod
    def get_id(self) -> str:
        pass
