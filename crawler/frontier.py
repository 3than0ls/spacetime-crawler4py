import time
from urllib.parse import urlparse
from utils import get_logger, get_urlhash, normalize, get_domain_name
import os
import shelve
import threading
import glob


THREAD_LOCK = threading.RLock()


class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self._config = config

        self._frontier = list()
        self._domains_last_accessed = {}

        if restart or os.getenv("TESTING") == "true" or not glob.glob(f"{self._config.save_file}*"):
            self._restart_save()
        else:
            self._load_save()

        # used in empty(), set in restart_save() or load_save()
        self._initial_url_count = len(self._frontier)

    def _restart_save(self):
        assert len(
            self._frontier) == 0, "_restart_save() only to be called during initialization"

        for file_path in glob.glob(f"{self._config.save_file}*"):
            if os.path.isfile(file_path):
                os.remove(file_path)

        self.logger.info(f"Starting from seed: {self._config.seed_urls}")
        for url in self._config.seed_urls:
            self.add_url(url)
            domain = get_domain_name(url)
            self._domains_last_accessed[domain] = 0


    def _load_save(self):
        if os.getenv("TESTING") == "true":
            return

        assert len(
            self._frontier) == 0, "_load_save() only to be called during initialization"

        with shelve.open(self._config.save_file) as seen_urls:
            for url_hash, (url, downloaded) in seen_urls.items():
                if not downloaded:
                    self._frontier.append(url)
                domain = get_domain_name(url)
                self._domains_last_accessed[domain] = 0
            self.logger.info(
                f"Starting from save in {self._config.save_file}. Added {len(self._frontier)} to frontier.")

    def _test_clear_seen_urls(self):
        with shelve.open(self._config.save_file) as seen_urls:
            seen_urls.clear()
            
    # def _sync_shelf(self):
    #     """Call this every once every period of time to sync shelf."""
    #     if os.getenv("TESTING") == "true":
    #         return

    #     with shelve.open(self._config.save_file) as seen_urls:
    #         seen_urls.update(self._seen_urls)
    #         seen_urls.sync()

    def _can_access_domain(self, domain):
        if domain not in self._domains_last_accessed:
            return True

        if time.time() - self._domains_last_accessed[domain] > self._config.time_delay:
            return True

        return False

    def _set_domain_seen(self, domain):
        self._domains_last_accessed[domain] = time.time()

    def _unsafe_get_tbd_url(self):
        """Get the next URL from the frontier in a potentially non-thread-safe manner."""
        if self.empty():
            return None

        try:
            for i in range(len(self._frontier)):
                index = -1-i
                current_url = self._frontier[index]
                domain = get_domain_name(current_url)
                if self._can_access_domain(domain):
                    self._set_domain_seen(domain)
                    del self._frontier[index]
                    return current_url
        except IndexError:
            return None

        return None

    def _unsafe_add_url(self, url):
        """
        Add the URL to the frontier
        """
        url = normalize(url)
        urlhash = get_urlhash(url)
        with shelve.open(self._config.save_file) as seen_urls:
            if urlhash not in seen_urls:
                seen_urls[urlhash] = (url, False)  # seen, but not downloaded
                self._frontier.append(url)

        # if urlhash not in self._seen_urls:
        #     self._seen_urls[urlhash] = (url, False)  # seen, but not downloaded
        #     self._frontier.append(url)

        # # save _seen_url to shelf every 50 URLs processed
        # if len(self._seen_urls) % 50 == 0:
        #     self._sync_shelf()

    def add_url(self, url):
        with THREAD_LOCK:
            self._unsafe_add_url(url)

    def url_seen(self, urlhash: str) -> bool:
        """Takes a URL hash and determines if it has been seen"""
        with shelve.open(self._config.save_file) as seen_urls:
            return urlhash in seen_urls
        # return urlhash in self._seen_urls

    def url_downloaded(self, urlhash: str) -> bool:
        """Takes a URL hash and determines if it has been downloaded"""
        with shelve.open(self._config.save_file) as seen_urls:
            return urlhash in seen_urls and seen_urls[urlhash][1]
        # return urlhash in self._seen_urls and self._seen_urls[urlhash][1]

    def empty(self):
        if os.getenv("TESTING") == "true":
            return len(self._frontier) == 0
        else:
            return len(self._frontier) == 0 and self._initial_url_count > len(self._config.seed_urls)

    def get_tbd_url(self):
        with THREAD_LOCK:
            return self._unsafe_get_tbd_url()

    def _unsafe_mark_url_complete(self, url):
        """
        Since the removal of the frontier save, this is no longer used.
        """
        urlhash = get_urlhash(url)
        with shelve.open(self._config.save_file) as seen_urls:
            seen_urls[urlhash] = (url, True)

            # if downloaded
            if not (urlhash in seen_urls and seen_urls[urlhash][1]):
                # This should not happen.
                message = f"Marking url {url} as complete, but have already downloaded it before."
                self.logger.error(message)
                assert False, message

            if urlhash not in seen_urls:
                # this should not happen either
                message = f"Marking url {url} as complete and downloaded, but have not seen it before."
                self.logger.warning(message)

        # if self.url_downloaded(urlhash):
        #     # This should not happen.
        #     message = f"Marking url {url} as complete, but have already downloaded it before."
        #     self.logger.error(message)
        #     assert False, message

        # if not self.url_seen(urlhash):
        #     # this should not happen either
        #     message = f"Marking url {url} as complete and downloaded, but have not seen it before."
        #     self.logger.warning(message)

        # self._seen_urls[urlhash] = (url, True)

    def mark_url_complete(self, url):
        with THREAD_LOCK:
            self._unsafe_mark_url_complete(url)
