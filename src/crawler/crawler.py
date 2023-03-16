from typing import List, Union
import requests
from queue import PriorityQueue
import logging as log

import re
from src.crawler.scraper.links import LinksScraper
from src.crawler.scraper.scraper import Scraper
import src.utils.constants as consts
from urllib.parse import urlsplit

from src.data_structure.graph.web import WebGraph


class WebSpider:
    def __init__(self, scrapers: List[Scraper], start_seed: str, max_depth: int = 5):
        self.scrapers = scrapers
        self._visited = set()
        self._unvisited = PriorityQueue()
        self._unvisited.put((0, self._process_url(start_seed)))  # The priority will later be set to be the depth of the url
        self._max_depth = max_depth
        self._links_scraper = LinksScraper()
        self._graph = WebGraph()

    def crawl(self) -> WebGraph:
        session = requests.Session()
        try:
            #  Crawls the web starting from the start_seed
            while not self._unvisited.empty() and len(self._visited) < self._max_depth:
                # Pop the first element from the queue to continue crawling
                depth, url = self._unvisited.get()

                # In order to prevent the same link from being visited twice if it is written in different ways:
                # https://www.example.com and http://www.example.com/
                # I will check both ways
                https_url = url.replace("http://", "https://")
                http_url = url.replace("https://", "http://")

                if https_url not in self._visited and http_url not in self._visited:

                    self._visited.add(url)

                    try:
                        log.info(f"Visiting url: {url}")
                        response = session.get(url)
                    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                        # ignore pages with errors and continue with next url
                        continue

                    # Get the links from the current url and add them to the queue
                    links = self._links_scraper.scrape(response)
                    for link in links:

                        if self._is_valid_url(link) and link not in self._visited:

                            # Add the link to the graph
                            # TODO: Think If I want to add the link to the graph
                            # self._add_edge(url, link, scraper=self._links_scraper)

                            # Add the link to the queue. The priority will be the depth of the link
                            self._unvisited.put((depth + 1, self._process_url(link)))

                    # Scrape the data from the current url using the predefined scrapers
                    for scraper in self.scrapers:
                        metadata = scraper.scrape(response)
                        # Add the metadata to the graph
                        self._add_edge(url, metadata, scraper=scraper)

            return self._graph

        except Exception as e:
            log.error(f"Error while crawling the web: {e}")

        finally:
            session.close()

    def _add_edge(self, url: str, data: Union[str, list, set], scraper: Scraper):
        """
        Add an edge to the graph. If the data is a string, add an edge to the url from the data. If the data is a list,
        add an edge to the url from each element in the list
        :param url: string. The url to add the edge to
        :param data: string or list. The data to add the edge from
        :param scraper: Scraper object. The scraper that scraped the data. Need it to get the weight of the edge
        :return:None
        """
        weight = scraper.get_weight() if scraper is not None else 0
        v_of_edge = [data] if isinstance(data, str) else data
        [self._graph.add_edge(v, url, weight=weight) for v in v_of_edge]

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        Check if the url is valid. Valid url is a url that has not have a file format at the end. We can look
        for a file format by looking for a dot in the end of url.
        :param url: string. The url to check
        :return: bool. True if the url is valid, False otherwise
        """
        match = re.findall(r"\.[a-zA-Z]{2,4}$", url)  # Look for a dot followed by 2-4 letters
        if not match:
            return True

        suffix = match[0]
        if suffix in consts.VALID_WEBSITE_SUFFIXES:
            return True

        return False

    @staticmethod
    def _extract_domain(url: str) -> str:
        """
        Extract the domain from the url
        :param url: string. The url to extract the domain from
        :return: string. The domain of the url
        """
        return urlsplit(url).netloc

    @staticmethod
    def _process_url(url: str) -> str:
        """
        Process the url and remove the unnecessary parts from it like www or / at the end
        :param url: string. The url to process
        :return: string. The processed url
        """
        return url.strip('/').replace("www.", "")