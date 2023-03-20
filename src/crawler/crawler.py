import asyncio
from typing import List

import requests
import logging as log

from src.data_structure.graph.callbacks.callback import GraphCallback
from src.crawler.filter import UrlFilter
from src.utils.config import Config
from src.utils.tools import clean_url, req_with_retry
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

    async def scrape(self, url: str) -> requests.Response:
        """
        Scrape the given urls for data.
         ***
         I tried using httpx but there is a bug in my pc or in the library that
        caused the event loop to crash. In order to fix it I had to use requests
        ***
        :param urls: url pool -> List of string [url1, url2, ...]. The urls will be scraped in concurrently
        :return: List of responses -> List of httpx.Response [response1, response2, ...]
        """
        try:
            session = req_with_retry(self._retries)
            response = session.get(url,
                # when crawling we should use generous timeout
                timeout=self._timeout,
                # we should use common web browser header values to avoid being blocked
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "accept-language": "en-US;en;q=0.9",
                    "accept-encoding": "gzip, deflate, br", # we should use encoding to save bandwidth
                }
            )
            return response

        except Exception as e:
            res = requests.Response()
            res.status_code = 500
            return res

    async def scrape_concurrently(self, urls: List[str]) -> List[requests.Response]:
        """
        Scrape the given urls for data.
         ***
         I tried using httpx but there is a bug in my pc or in the library that
        caused the event loop to crash. In order to fix it I had to use requests
        ***
        :param urls: url pool -> List of string [url1, url2, ...]. The urls will be scraped in concurrently
        :return: List of responses -> List of httpx.Response [response1, response2, ...]
        """
        responses, failures = [], []
        # To not put too much stress on the internet connection we will scrape the urls in batches
        for next_batch in range(0, len(urls), self._max_requests):
            for response in await asyncio.gather(*[self.scrape(url) for url in urls[next_batch:next_batch + self._max_requests]]):
                if response.status_code == 200:
                    responses.append(response)
                else:
                    failures.append(response)

        return responses

    def parse_for_urls(self, responses: List[requests.Response]) -> List[str]:
        """
        Parse the given responses for urls
        :param responses: List of httpx.Response [response1, response2, ...]
        :return: List of urls -> List of string [url1, url2, ...]
        """
        scraped_results = []

        for response in responses:
            scraped_results.extend(self._url_parser.parse(response))

        log.info(f"Found {len(scraped_results)} urls in the responses")

        urls = []
        for res in scraped_results:
            # Try to filter the url based on rules. If it came back empty it means that the url is not valid
            if self._filter.filter([res.data]):
                # Need to add the url to the data structure. The data structure will know how to handle the data.
                # Each data structure has its own way of handling the data
                self._data_structure.add(res)
                urls.append(res.data)

        return urls

    async def callbacks(self, responses: List[requests.Response]) -> None:
        """
        Run the callbacks on the given responses
        :param responses: List of Responses [response1, response2, ...]
        :return: None
        """
        for callback in self._callbacks:
            for response in responses:
                callback.process(graph=self._data_structure, data=response)

    async def crawl(self) -> WebGraph:
        """
        Crawl the web starting from the given seed
        :return:
        """
        depth = 0
        url_pool = [self._start_seed]
        try:
            while url_pool and depth <= self._max_depth:
                responses = await self.scrape_concurrently(urls=url_pool)
                url_pool = self.parse_for_urls(responses=responses)
                await self.callbacks(responses=responses)

                depth += 1

            if depth > self._max_depth:
                log.warning(f"Reached max depth of {self._max_depth}. Stop crawling")

            return self._data_structure

        except Exception as e:
            log.error(f"Error while crawling the web: {e}")
            raise e
