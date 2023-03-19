from typing import List, Pattern
import posixpath
from urllib.parse import urlparse

from tldextract import tldextract
from w3lib.url import canonicalize_url
import logging as log
import src.utils.constants as consts
from src.utils.tools import extract_base_url


class UrlFilter:

    def __init__(self, config: dict) -> None:
        domain = config.get(consts.DOMAIN_FILTER)
        subdomain = config.get(consts.SUBDOMAIN_FILTER)
        follow = config.get(consts.PATTERN_RULES)
        # restrict filtering to specific TLD
        self.domain = domain
        # restrict filtering to sepcific subdomain
        self.subdomain = subdomain
        self.follow = follow or []
        log.info(f"filter created for domain {self.subdomain}.{self.domain} with follow rules {follow}")
        self.seen = set()

    def is_valid_ext(self, url):
        """ignore non-crawlable documents"""
        return posixpath.splitext(urlparse(url).path)[1].lower() not in consts.IGNORED_EXTENSIONS

    def is_valid_scheme(self, url):
        """ignore non http/s links"""
        return urlparse(url).scheme in ['https', 'http']

    def is_valid_domain(self, url):
        """ignore offsite urls"""
        if not self.domain and not self.subdomain:
            return True
        parsed = tldextract.extract(url)
        return parsed.registered_domain == self.domain and parsed.subdomain == self.subdomain

    def is_valid_path(self, url):
        """ignore urls of undesired paths"""
        if not self.follow:
            return True
        path = urlparse(url).path
        for pattern in self.follow:
            if pattern.match(path):
                return True
        return False

    def is_new(self, url):
        """ignore visited urls (in canonical form)"""
        return extract_base_url(url) not in self.seen

    def filter(self, urls: List[str]) -> List[str]:
        """filter list of urls"""
        found = []
        for url in urls:
            if not self.is_valid_scheme(url):
                log.debug(f"drop ignored scheme {url}")
                continue
            if not self.is_valid_domain(url):
                log.debug(f"drop domain missmatch {url}")
                continue
            if not self.is_valid_ext(url):
                log.debug(f"drop ignored extension {url}")
                continue
            if not self.is_valid_path(url):
                log.debug(f"drop ignored path {url}")
                continue
            if not self.is_new(url):
                log.debug(f"drop duplicate {url}")
                continue
            self.seen.add(canonicalize_url(url))
            found.append(url)
        return found

    def is_valid(self, scraped_res):
        url = scraped_res.data
        answer = all((
            self.is_valid_scheme(url),
            self.is_valid_domain(url),
            self.is_valid_ext(url),
            self.is_valid_path(url),
            self.is_new(url)),
        )
        self.seen.add(extract_base_url(url))
        return answer
