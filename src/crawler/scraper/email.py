from src.crawler.scraper.scraper import Scraper, ScraperResult
import src.utils.constants as consts
import re
from bs4 import BeautifulSoup
from requests import Response
import logging as log
from src.utils.tools import extract_domain, extract_base_url, EMAIL_REGEX

class EmailScraper(Scraper):

    def scrape(self, response: Response) -> ScraperResult:
        soup = BeautifulSoup(response.content, 'html.parser')

        emails = set()
        for match in re.finditer(EMAIL_REGEX, soup.get_text()):
            emails.add(match.group())

        if len(emails) > 0:
            log.info(f"Found {len(emails)} emails in url: {response.url}")

        return ScraperResult(extract_domain(response.url), extract_base_url(response.url), emails, self.get_id())

    def get_id(self) -> str:
        return consts.EMAIL_TYPE_TOKEN
