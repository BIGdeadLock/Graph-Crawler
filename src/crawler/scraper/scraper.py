from abc import ABC, abstractmethod

from requests import Response
from collections import namedtuple

ScraperResult = namedtuple('ScraperResult', ['domain', 'url','data','type'])

class Scraper(ABC):

    @abstractmethod
    def scrape(self, response: Response) -> ScraperResult:
        pass

    @abstractmethod
    def get_id(self) -> str:
        pass
