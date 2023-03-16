from src.crawler.scraper.scraper import Scraper
import src.utils.constants as consts
import re
from bs4 import BeautifulSoup
from requests import Response

class EmailScraper(Scraper):

    def scrape(self, response: Response) -> set:
        soup = BeautifulSoup(response.content, 'html.parser')
        email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+" # Get all string in the format of email
        emails = set()
        for match in re.finditer(email_regex, soup.get_text()):
            emails.add(match.group())

        return emails

    def get_id(self) -> str:
        return consts.EMAIL_SCRAPER_TOKEN

    def get_weight(self) -> int:
        return 1
