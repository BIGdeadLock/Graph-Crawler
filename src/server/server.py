
from typing import List
from joblib import Parallel, delayed
from src.crawler.scraper.links import LinksScraper
from src.crawler.scraper.scraper import Scraper
from src.crawler.scraper import SCRAPERS
from src.utils.config import Config
from src.utils.singleton import singleton
from src.crawler.crawler import WebSpider
import src.utils.constants as consts
from src.data_structure.graph.ds import combine_graphs, load_graph, save_graph, serialize_graph


@singleton
class ServerInterface(object):
    def __init__(self, **kwargs):
        self._config: Config = kwargs.get('config', Config())
        self.crawlers = None
        self.graph = load_graph(consts.GRAPH_OUTPUT_FILE_PATH)

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

        max_depth = self._config.get(consts.CRAWLER_SECTION, consts.MAX_DEPTH_CONFIG_TOKEN, return_as_string=False)

        scrapers_name = content.get(consts.SCRAPERS_CONFIG_TOKEN, None)
        scrapers = self.get_scrapers(names=scrapers_name)

        self.crawlers = [WebSpider(scrapers=scrapers, start_seed=seed, max_depth=max_depth) for seed in seeds]
        res = [crawler.crawl() for crawler in self.crawlers]
        # # Start a separate thread for each crawler to start crawling from a different seed
        # n_jobs = self._config.get(consts.SYSTEM_SECTION, consts.NUMBER_OF_JOBS_CONFIG_TOKEN, return_as_string=False)
        # res = Parallel(n_jobs=n_jobs, backend="threading")(delayed(crawler.crawl)() for crawler in self.crawlers)
        self.graph = combine_graphs(res)
        save_graph(consts.GRAPH_OUTPUT_FILE_PATH, self.graph)
        return serialize_graph(self.graph)

    def get_scrapers(self, names: List[str]) -> List[Scraper]:
        """
       Dynamically create scrapers based on the config file
       :return: List of scrapers all inheriting from Scraper
       """
        # If the user didn't specify any scrapers, use the config default
        if not names:
            names = self._config.get_scrapers()

        scrapers = []
        for scraper_name in names:
            for scraper in SCRAPERS:
                if scraper.get_id() == scraper_name:
                    scrapers.append(scraper)

        scrapers.append(LinksScraper())
        return scrapers

    def get_top_urls(self, n=5) -> list:
        """
        Get the top urls from the crawlers for each domain
        :return: list of dict {domain: List of urls}
        """
        return self.graph.get_top_n_for_each_domain(n)

