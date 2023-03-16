from abc import ABC, abstractmethod

from requests import Response
from collections import namedtuple

ScraperResult = namedtuple('ScraperResult', ['data', 'weight', 'scraper_id'])

class Scraper(ABC):

    @abstractmethod
    def scrape(self, response: Response) -> ScraperResult:
        pass

    @abstractmethod
    def get_weight(self) -> int:
        pass

    @abstractmethod
    def get_id(self) -> str:
        pass
