
from src.data_structure.graph.callbacks.callback import CallbackResult, GraphCallback
import src.utils.constants as consts
import re
from bs4 import BeautifulSoup
from httpx import Response

from src.utils.tools import extract_domain, extract_base_url, EMAIL_REGEX


class EmailParser(GraphCallback):


    def process(self, graph, data):
        soup = BeautifulSoup(data.content, 'html.parser')

        for match in re.finditer(EMAIL_REGEX, soup.get_text()):
            res = CallbackResult(extract_domain(data.url), extract_base_url(data.url),
                               match.group(), self.get_id())
            graph.add(res)

    @staticmethod
    def get_id() -> str:
        return consts.EMAIL_TYPE_TOKEN
