from typing import List

from src.utils.tools import extract_domain, extract_base_url, is_valid_url, clean_url
from src.data_structure.graph.callbacks.callback import CallbackResult
import src.utils.constants as consts
from bs4 import BeautifulSoup
from requests import Response


class URLsParser:

    def parse(self, response: Response) -> List[CallbackResult]:
        """
        Scrape the response and look for links in the html to other urls
        :param response: request.Response object. Response from the url
        :return: list of links to other urls (including duplicates)
        """
        soup = BeautifulSoup(response.content, 'html.parser')
        result = []
        for link in soup.find_all('a'):
            href = link.get('href')  # Get the href attribute of the link which points to the url
            if href is not None and href.startswith('http') and is_valid_url(href):
                clean_link = clean_url(href)
                result.append(
                    CallbackResult(extract_domain(response.url), extract_base_url(response.url),
                                   clean_link, self.get_id())
                )

        return result

    def get_id(self) -> str:
        return consts.URL_TYPE_TOKEN
