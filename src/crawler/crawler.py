# from gevent import monkey
# monkey.patch_all(thread=False, select=False)
import grequests
import requests


import asyncio
from typing import List
import logging as log

from src.data_structure.graph.callbacks.callback import GraphCallback
from src.crawler.filter import UrlFilter
from src.utils.config import Config
from src.utils.tools import clean_url#, req_with_retry
from src.crawler.parsers.url import URLsParser
import src.utils.constants as consts
from src.data_structure.graph.graph import WebGraph


class WebSpider:
    def __init__(self, callbacks: List[GraphCallback], url_filter: UrlFilter, start_seed: str, config: Config):
        self._callbacks = callbacks
        self._filter = url_filter
        self._start_seed = clean_url(start_seed)
        self._data_structure = WebGraph(config=config)
        self._url_parser = URLsParser()
        self._max_depth = config.get(consts.CRAWLER_SECTION, consts.MAX_DEPTH_CONFIG_TOKEN, return_as_string=False)
        self._retries = config.get(consts.CRAWLER_SECTION, consts.MAX_RETIRES_CONFIG_TOKEN, return_as_string=False)
        self._timeout = config.get(consts.CRAWLER_SECTION, consts.TIMEOUT_CONFIG_TOKEN, return_as_string=False)
        self._max_requests = config.get(consts.CRAWLER_SECTION, consts.MAX_REQUEST_CONFIG_TOKEN, return_as_string=False)
        log.warning(f"Max depth is set to {self._max_depth}")
        self._stop_scaling_up = False


    def parse_for_url(self, response: requests.Response) -> List[str]:
        """
        Parse the given responses for urls
        :param response: Http response to scrape from
        :return: List of urls -> List of string [url1, url2, ...]
        """

        urls = []
        for res in self._url_parser.parse(response):
            # Try to filter the url based on rules. If it came back empty it means that the url is not valid
            if self._filter.filter([res.data]):
                # Need to add the url to the data structure. The data structure will know how to handle the data.
                # Each data structure has its own way of handling the data
                self._data_structure.add(res)
                urls.append(res.data)

        log.debug(f"Found {len(urls)} urls in the responses")
        return urls

    async def callbacks(self, response: requests.Response) -> None:
        """
        Run the callbacks on the given responses. The callbacks will be run in a sequential manner
        :param response: Http responses to run the callbacks on. Need to have a content attribute
        :return:
        """
        for callback in self._callbacks:
            callback.process(graph=self._data_structure, data=response)

    async def crawl(self) -> WebGraph:
        """
        Crawl the web starting from the given seed. The search is done in a BFS manner and will stop when the max depth
        is reached or when there are no more urls to crawl.
        :return: WebGraph object
        """
        depth = 0
        url_pool = [self._start_seed]
        try:
            while url_pool and depth <= self._max_depth:
                for response in grequests.imap(
                        [grequests.get(url, timeout=self._timeout) for url in url_pool], size=self._max_requests
                ):
                    if response.status_code == 429:

                        log.warning(f"Got 429 response from {response.url}. Waiting for 5 seconds")
                        await asyncio.sleep(2)
                        log.warning("Trying to scaling down the requests")
                        self._max_requests = self._max_requests // 2
                        self._stop_scaling_up = True

                    url_pool = self.parse_for_url(response=response)
                    await self.callbacks(response=response)

                if not self._stop_scaling_up:
                    log.info("Scaling up the number of requests")
                    self._max_requests = self._max_requests + 5

                depth += 1

            if depth > self._max_depth:
                log.warning(f"Reached max depth of {self._max_depth}. Stop crawling")

            return self._data_structure

        except Exception as e:
            log.error(f"Error while crawling the web: {e}")
            raise e
