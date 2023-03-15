from typing import List
import requests
from queue import PriorityQueue
import logging as log

from src.crawler.scraper.links import LinksScraper
from src.crawler.scraper.scraper import Scraper

class WebCrawler:
    def __init__(self, scrapers: List[Scraper], start_seed: str, max_depth: int = 5):
        self.scrapers = scrapers
        self._visited = set()
        self._unvisited = PriorityQueue()
        self._unvisited.put((0, start_seed))  # The priority will later be set to be the depth of the url
        self._max_depth = max_depth
        self._links_scraper = LinksScraper()
        self._data = {}

    def crawl(self) -> dict:
        session = requests.Session()
        try:
            #  Crawls the web starting from the start_seed
            while not self._unvisited.empty() and len(self._visited) < self._max_depth:
                # Pop the first element from the queue to start crawling
                depth, url = self._unvisited.get()
                # Check if the url has already been visited to not visit it again
                if url not in self._visited:
                    self._visited.add(url)

                    response = session.get(url)

                    # Get the links from the current url and add them to the queue
                    links = self._links_scraper.scrape(response)
                    for link in links:
                        if link not in self._visited:
                            self._unvisited.put((depth + 1, link))

                    # Scrape the data from the current url using the predefined scrapers
                    for scraper in self.scrapers:
                        metadata = scraper.scrape(response)
                        # TODO: Add the metadata to the data dictionary and think about the graph structure

            return self._data

        except Exception as e:
            log.error(f"Error while crawling the web: {e}")

        finally:
            session.close()

