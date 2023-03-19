
from src.data_structure.graph.callbacks.callback import CallbackResult, Callback, GraphCallback
import src.utils.constants as consts
import re
from bs4 import BeautifulSoup
from httpx import Response
import logging as log

from src.data_structure.graph.graph import WebGraph
from src.utils.tools import extract_domain, extract_base_url, EMAIL_REGEX


class EmailParser(GraphCallback):


    def process(self, graph: WebGraph, response: Response):
        soup = BeautifulSoup(response.content, 'html.parser')

        for match in re.finditer(EMAIL_REGEX, soup.get_text()):

            res = CallbackResult(extract_domain(response.url), extract_base_url(response.url),
                               match.group(), self.get_id())
            graph.add(res)

    @staticmethod
    def get_id() -> str:
        return consts.EMAIL_TYPE_TOKEN
