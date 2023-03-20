import asyncio
from typing import List, Dict
from joblib import Parallel, delayed

from src.data_structure.graph.callbacks.callback import GraphCallback
from src.crawler.filter import UrlFilter
from src.data_structure.graph.callbacks import CALLBACKS
from src.utils.config import Config
from src.utils.singleton import singleton
from src.crawler.crawler import WebSpider
import src.utils.constants as consts
from src.data_structure.graph.graph import combine_graphs, load_graph, save_graph, serialize_graph
import logging as log


@singleton
class ServerInterface(object):
    def __init__(self, **kwargs):
        self._config: Config = kwargs.get('config', Config())
        self.crawlers = None
        try:
            self.graph = load_graph(consts.GRAPH_OUTPUT_FILE_PATH)
        except Exception:
            self.graph = None
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()

    async def build_graph(self, content: dict) -> dict:
        """
        The method starts the crawling process and returns the graph
        Build a graph from the given seeds and scrapers
        :param content: request in the format of {seeds: [seed1, seed2, ...], scrapers: [scraper1, scraper2, ...]}
        :return: graph like structure
        """
        seeds = content.get(consts.SEEDS_CONFIG_TOKEN, None)
        if not seeds:
            # If the user didn't specify any seeds, use the config default to start the crawling
            seeds = self._config.get_seeds()

        nodes_types = content.get(consts.REQUEST_NODES_TOKEN, None)
        callbacks = self._get_callbacks(nodes_types=nodes_types)

        self.crawlers = [
            WebSpider(callbacks=callbacks,
                      url_filter=UrlFilter(self._config.get_section(consts.FILTERS_SECTION)),
                      start_seed=seed, config=self._config)
            for seed in seeds]

        # Start a separate thread for each crawler to start crawling from a different seed
        n_jobs = self._config.get(consts.SYSTEM_SECTION, consts.NUMBER_OF_JOBS_CONFIG_TOKEN, return_as_string=False)
        res = Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(self._async_crawling)(self.loop, crawler=crawler) for crawler in self.crawlers
        )

        self.graph = combine_graphs(res)
        save_graph(consts.GRAPH_OUTPUT_FILE_PATH, self.graph)
        return serialize_graph(self.graph)

    def get_top_urls(self, n=5) -> list:
        """
        Get the top urls from the crawlers for each domain
        :return: list of dict {domain: List of urls}
        """
        return self.graph.get_top_n_for_each_domain(n)

    def _get_callbacks(self, nodes_types: List[str]) -> List[GraphCallback]:
        """
       Dynamically create callbacks from the given nodes types of the user or configuration
       :return: List of scrapers all inheriting from Scraper
       """
        # If the user didn't specify any scrapers, use the config default
        if not nodes_types:
            nodes_types = self._config.get_callbacks()

        return [CALLBACKS[n_type] for n_type in nodes_types if n_type in CALLBACKS]

    @staticmethod
    def _async_crawling(loop: asyncio.AbstractEventLoop, **kwargs):
        asyncio.set_event_loop(loop)
        try:
            crawler = kwargs.get('crawler')
            return asyncio.run(crawler.crawl())
        except Exception as e:
            log.error('Crawling loop got exception.', e)


