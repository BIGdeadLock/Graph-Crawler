from urllib.parse import urljoin

from src.crawler.scraper.scraper import Scraper
import src.utils.constants as consts

from bs4 import BeautifulSoup
from requests import Response


class LinksScraper(Scraper):

    def scrape(self, response: Response) -> list:
        """
        Scrape the response and look for links in the html to other urls
        :param response: request.Response object. Response from the url
        :return: list of links to other urls (including duplicates)
        """
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')  # Get the href attribute of the link which points to the url
            if href is not None and href.startswith('http'):
                links.append(href)

        return links

    def get_id(self) -> str:
        return consts.LINKS_SCRAPER_TOKEN
