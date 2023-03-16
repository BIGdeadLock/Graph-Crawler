from typing import List
from joblib import Parallel, delayed
from src.crawler.scraper.scraper import Scraper
from src.crawler.scraper import SCRAPERS
from src.utils.config import Config
from src.utils.singleton import singleton
from src.crawler.crawler import WebSpider
import src.utils.constants as consts
from src.data_structure.graph.web import combine_graphs
import networkx as nx
import jsonpickle
from jinja2 import Template
import logging as log

@singleton
class ServerInterface(object):
    def __init__(self, **kwargs):
        self._config: Config = kwargs.get('config', Config())
        self.crawlers = None

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

        scrapers_name = content.get(consts.SCRAPERS_CONFIG_TOKEN, None)
        scrapers = self.get_scrapers(names=scrapers_name)
        self.crawlers = [WebSpider(scrapers=scrapers, start_seed=seed) for seed in seeds]
        res = [crawler.crawl() for crawler in self.crawlers]
        # # Start a separate thread for each crawler to start crawling from a different seed
        # n_jobs = self._config.get(consts.SYSTEM_SECTION, consts.NUMBER_OF_JOBS_CONFIG_TOKEN, return_as_string=False)
        # res = Parallel(n_jobs=n_jobs, backend="threading")(delayed(crawler.crawl)() for crawler in self.crawlers)
        graph = combine_graphs(res)
        self.save_graph_as_html(graph)
        return nx.adjacency_data(graph)

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
        return scrapers

    @staticmethod
    def save_graph_as_html(graph):
        data = nx.readwrite.json_graph.node_link_data(graph)

        # serialize the JSON data
        json_str = jsonpickle.encode(data)

        # load the template file
        with open(consts.TEMPLATE_PATH, 'r') as f:
            template_str = f.read()

        # create a Jinja2 template
        template = Template(template_str)

        # render the template with the JSON data
        html_str = template.render(json_str=json_str)

        log.info(f"Saving graph to {consts.GRAPH_TEMPLATE_PATH}")
        with open(consts.GRAPH_TEMPLATE_PATH, 'w') as f:
            f.write(html_str)