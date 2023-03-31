import time

import httpx
import requests
import joblib

import asyncio
from typing import List, Generator
import logging as log

from src.data_structure.graph.callbacks.callback import GraphCallback
from src.crawler.filter import UrlFilter
from src.utils.config import Config
from src.utils.tools import clean_url, os
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
        self._headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US;en;q=0.9",
            "accept-encoding": "gzip, deflate, br",
        }
        self._max_threads = os.cpu_count() * 2

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

    async def crawl(self, start_seed=None) -> WebGraph:
        """
        Crawl the web starting from the given seed. The search is done in a BFS manner and will stop when the max depth
        is reached or when there are no more urls to crawl.
        :param start_seed: Url to start crawling from
        :return: WebGraph object
        """
        depth = 0

        if not start_seed:
            start_seed = [self._start_seed]

        url_pool = start_seed
        try:
            while url_pool and depth <= self._max_depth:
                for response in self.imap(url_pool):

                    if self._max_requests > self._max_threads:
                        log.warning(
                            f"Max requests is bigger than the number of threads. Setting max requests to {self._max_threads}")
                        self._max_requests = self._max_threads

                    elif response.status_code == 429:

                        log.warning(f"Got 429 response from {response.url}. Waiting for 5 seconds")
                        await asyncio.sleep(5)
                        log.warning("Trying to scaling down the requests")
                        self._max_requests = self._max_requests // 2
                        self._stop_scaling_up = True

                    elif response.status_code != 200:
                        log.warning(f"Got {response.status_code} response from {response.url}. Skipping")
                        continue

                    url_pool = self.parse_for_url(response=response)
                    await self.callbacks(response=response)

                if not self._stop_scaling_up:
                    log.info("Scaling up the number of requests")
                    self._max_requests = self._max_requests + 5

                depth += 1

            if depth > self._max_depth:
                log.warning(f"Reached max depth of {self._max_depth}. Stop crawling")

            return self._data_structure

        except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout) as e:
            log.warning(f"Got timeout exception. Waiting for 5 seconds")
            await asyncio.sleep(5)
            log.warning("Trying to scaling down the requests")
            self._max_requests = self._max_requests // 2
            if self._max_requests == 0:
                log.error("Max requests is 0. No more requests can be sent. Returning the current graph")
                return self._data_structure

            self._stop_scaling_up = True
            await self.crawl(start_seed=url_pool)

        except Exception as e:
            log.error(f"Error while crawling the web: {e}")
            raise e

    def imap(self, url_pool) -> Generator:
        tasks = [
            (self.send_request, {"url": url})
            for url in url_pool
        ]
        res = joblib.Parallel(n_jobs=self._max_requests, backend="threading")(
            joblib.delayed(task[0])(**task[1]) for task in tasks)

        for r in res:
            yield r

    def send_request(self, url):
        try:
            response = httpx.request(method="GET", url=url, headers=self._headers, timeout=self._timeout, verify=False)
            return response
        except Exception as e:
            log.error(f"Error while sending request to {url}: {e}")
            return httpx.Response(status_code=500, request=httpx.Request("GET", url), content=b"")
