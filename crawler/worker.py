from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from deliverables import Deliverable
from crawler import Frontier
import random


class Worker(Thread):
    def __init__(self, worker_id, config, frontier: Frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.worker_id = worker_id
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {
            "from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import",
                                                         "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"

        self.deliverable = Deliverable(deliverable_id=worker_id)

        super().__init__(daemon=True)

    def run(self):
        while True:
            try:
                tbd_url = self.frontier.get_tbd_url()
                if not tbd_url:
                    if self.frontier.empty():
                        self.logger.info(
                            "Frontier is empty. Stopping Crawler.")
                        break
                    else:  # frontier is not empty, but no URLs are allowed to be downloaded
                        # for some reason this is never being logged? weird
                        self.logger.info(
                            "Respecting politeness delay since there are no free links to download. Idling Crawler.")
                        time.sleep(self.config.time_delay)
                        continue
            except RuntimeError as E:
                self.logger.warning(
                    f"Worker {self.worker_id} encountered a race condition. Waiting...")
                time.sleep(self.config.time_delay + random.random())
                continue

            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, self.deliverable)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        self.logger.critical(f"Worker {self.worker_id} shutting down.")
