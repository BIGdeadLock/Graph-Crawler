from src.crawler.scraper.scraper import Scraper, ScraperResult
import src.utils.constants as consts
import re
from bs4 import BeautifulSoup
from requests import Response
import logging as log

class EmailScraper(Scraper):

    def scrape(self, response: Response) -> ScraperResult:
        soup = BeautifulSoup(response.content, 'html.parser')
        email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+" # Get all string in the format of email
        emails = set()
        for match in re.finditer(email_regex, soup.get_text()):
            emails.add(match.group())

        if len(emails) > 0:
            log.info(f"Found {len(emails)} emails in url: {response.url}")

        return ScraperResult(emails, self.get_weight(), self.get_id())

    def get_id(self) -> str:
        return consts.EMAIL_SCRAPER_TOKEN

    def get_weight(self) -> int:
        return 1
