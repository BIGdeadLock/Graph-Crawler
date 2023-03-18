
from src.utils.tools import extract_domain, extract_base_url, is_valid_url, clean_url
from src.crawler.scraper.scraper import Scraper, ScraperResult
import src.utils.constants as consts

from bs4 import BeautifulSoup
from requests import Response


class URLsScraper(Scraper):

    def scrape(self, response: Response) -> ScraperResult:
        """
        Scrape the response and look for links in the html to other urls
        :param response: request.Response object. Response from the url
        :return: list of links to other urls (including duplicates)
        """
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')  # Get the href attribute of the link which points to the url
            if href is not None and href.startswith('http') and is_valid_url(href):
                links.append(clean_url(href))

        return ScraperResult(extract_domain(response.url), extract_base_url(response.url), links, self.get_id())

    def get_id(self) -> str:
        return consts.URL_TYPE_TOKEN
