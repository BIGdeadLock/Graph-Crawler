from typing import List, Union
import requests
from queue import PriorityQueue
import logging as log

from src.utils.tools import is_valid_url,extract_base_url, clean_url
from src.crawler.scraper.scraper import Scraper
import src.utils.constants as consts

from src.data_structure.graph.ds import WebGraph
from joblib import Parallel, delayed


class WebSpider:
    def __init__(self, scrapers: List[Scraper], start_seed: str, max_depth: int = 5):
        self.scrapers = scrapers
        self._visited = set()
        self._unvisited = PriorityQueue()
        self._unvisited.put(
            (0, clean_url(start_seed)))  # The priority will later be set to be the depth of the url
        self._max_depth = max_depth
        log.warning(f"Max depth is set to {self._max_depth}")
        self._data_structure = WebGraph()

    def crawl(self) -> WebGraph:
        session = requests.Session()
        try:
            #  Crawls the web starting from the start_seed
            while not self._unvisited.empty():
                # Pop the first element from the queue to continue crawling
                depth, url = self._unvisited.get()

                if depth > self._max_depth:
                    log.warning(f"Reached max depth of {self._max_depth}. Stop crawling")
                    break

                base_url = extract_base_url(url)  # Use to extract the base url from the url

                if base_url not in self._visited:
                    self._visited.add(base_url)

                    try:
                        log.info(f"Visiting url: {url}, depth: {depth}")
                        response = session.get(url)
                    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                        log.warning(f"Could not connect to url: {url}. Continue with next url")
                        # ignore pages with errors and continue with next url
                        continue

                    n_jobs = len(self.scrapers)
                    res = Parallel(n_jobs=n_jobs, backend="threading")(
                        delayed(scraper.scrape)(response)
                        for scraper in self.scrapers
                    )

                    for scraped_res in res:
                        # Add all the scraped data to the data structure. It knows how to handle the type of data
                        # it gets so no need to check here
                        self._data_structure.add_scraped_data(scraped_res)
                        # Special case is the links extracted from the scraped data. We need to add them to the queue
                        if scraped_res.type == consts.URL_TYPE_TOKEN:
                            for link in scraped_res.data:
                                if link not in self._visited:
                                    self._unvisited.put((depth + 1, link))

            return self._data_structure

        except Exception as e:
            log.error(f"Error while crawling the web: {e}")

        finally:
            session.close()





