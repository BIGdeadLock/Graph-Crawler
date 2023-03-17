from typing import List, Union
import requests
from queue import PriorityQueue
import logging as log

import re
from src.crawler.scraper.scraper import Scraper
import src.utils.constants as consts
from urllib.parse import urlsplit

from src.data_structure.graph.ds import WebGraph
from joblib import Parallel, delayed


class WebSpider:
    def __init__(self, scrapers: List[Scraper], start_seed: str, max_depth: int = 5):
        self.scrapers = scrapers
        self._visited = set()
        self._unvisited = PriorityQueue()
        self._unvisited.put(
            (0, self._clean_url(start_seed)))  # The priority will later be set to be the depth of the url
        self._max_depth = max_depth
        log.warning(f"Max depth is set to {self._max_depth}")
        self._graph = WebGraph()
        self._domains = set()
        self._current_domain = None  # Placeholder for the current domain

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

                self._current_domain = self._extract_domain(url)  # Use to extract the domain from the url
                base_url = self._extract_base_url(url)  # Use to extract the base url from the url

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
                        self._add_nodes(scraped_res=scraped_res)

                        if scraped_res.scraper_id == consts.LINKS_SCRAPER_TOKEN:
                            self._handle_scraped_links(url, scraped_res, depth)
                        else:
                            self._handle_scraped_data(url, scraped_res)

            return self._graph

        except Exception as e:
            log.error(f"Error while crawling the web: {e}")

        finally:
            session.close()

    def _add_edge(self, url: str, data: Union[str, list, set], weight: int, scraper: Scraper = None):
        """
        Add an edge to the graph. If the data is a string, add an edge to the url from the data. If the data is a list,
        add an edge to the url from each element in the list
        :param url: string. The url to add the edge to
        :param data: string or list. The data to add the edge from
        :param scraper: Scraper object. The scraper that scraped the data. Need it to get the weight of the edge
        :return:None
        """
        weight = weight if scraper is None else scraper.get_weight()
        v_of_edge = [data] if isinstance(data, str) else data
        [self._graph.add_edge(v, url, weight=weight) for v in v_of_edge]

    def _add_nodes(self, scraped_res):
        """
        Add the nodes to the graph with the appropriate attributes
        :param scraped_res: ScraperResult object. The scraped data
        :return:
        """
        data = scraped_res.data if isinstance(scraped_res.data, (list, set)) else [scraped_res.data]
        for v in data:
            self._graph.add_node(v)
            self._graph.add_domain_attr_to_node(v, self._current_domain)
            self._graph.add_type_attr_to_node(v, scraped_res.scraper_id)

    def _handle_scraped_links(self, url, scraped_res, depth):
        """
        Handle the scraped links. Add the links to the graph and to the queue
        :param url: url the link was scraped from
        :param scraped_res: ScraperResult object. The scraped links
        :param depth: int. The depth of the url
        :return:
        """
        # For links scraper, the data is a list of links
        links = scraped_res.data
        for link in links:
            if self._is_valid_url(link) and link not in self._visited:
                # Add the link to the graph
                self._add_edge(url, link, weight=scraped_res.weight)

                # Add the link to the queue. The priority will be the depth of the link
                self._unvisited.put((depth + 1, self._clean_url(link)))

    def _handle_scraped_data(self, url, scraped_res):
        """
        Handle the scraped data. Add the data to the graph
        :param url: String. The url to add the edge to
        :param scraped_data: list of items
        :return:
        """
        self._add_edge(url, scraped_res.data, weight=scraped_res.weight)

    def _extract_domain(self, url: str) -> str:
        """
        Extract the domain from the url
        :param url: string. The url to extract the domain from
        :return: string. The domain of the url
        """
        domain = urlsplit(url).netloc
        if domain not in self._domains:
            self._domains.add(domain)

        return domain

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
    def _extract_base_url(url: str) -> str:
        """
        Extract the base url from the url. For example: https://www.example.com/bla/bla/bla -> example.com/bla/bla/bla
        :param url: string. The url to extract the base url from
        :return: string. The base url of the url
        """
        return urlsplit(url).netloc + urlsplit(url).path

    @staticmethod
    def _clean_url(url: str) -> str:
        """
        Process the url and remove the unnecessary parts from it like www or / at the end
        :param url: string. The url to process
        :return: string. The processed url
        """
        return url.strip('/').replace("www.", "")
