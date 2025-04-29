import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize, get_domain_name
from scraper import is_valid

from urllib.parse import urlparse
import time
import threading

THREAD_LOCK = threading.Lock()


class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self._config = config
        self._frontier = list()

        # a set of URLs (hashed) that have been seen
        self._seen = set()

        # skip the frontier
        self.logger.info("Starting from seed: {self.config.seed_urls}")
        for url in self._config.seed_urls:
            self.add_url(url)

        # maintain a map of unique domain names to time accessed
        self._domains_last_accessed = {}
        for url in self._frontier:
            domain = get_domain_name(url)
            self._domains_last_accessed[domain] = 0

    def empty(self):
        return len(self._frontier) == 0

    def _can_access_domain(self, domain):
        if domain not in self._domains_last_accessed:
            return True

        if time.time() - self._domains_last_accessed[domain] > self._config.time_delay:
            return True

        return False

    def _set_domain_seen(self, domain):
        with THREAD_LOCK:
            self._domains_last_accessed[domain] = time.time()

    def get_tbd_url(self):
        """Get the next URL from the frontier"""
        if self.empty():
            return None

        for i in range(len(self._frontier)):
            index = -1-i
            current_url = self._frontier[index]
            domain = get_domain_name(current_url)

            if self._can_access_domain(domain):
                self._set_domain_seen(domain)
                self._frontier.pop(index)
                assert domain in self._domains_last_accessed
                return current_url

        return None

    def add_url(self, url):
        """
        Add the URL to the frontier
        """
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self._seen:
            self._frontier.append(url)

    def mark_url_complete(self, url):
        """
        Since the removal of the frontier save, this is no longer used.
        """
        urlhash = get_urlhash(url)
        if urlhash not in self._seen:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self._seen.append(urlhash)
