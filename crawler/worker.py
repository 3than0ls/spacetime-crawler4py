from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from deliverables import RawDeliverableData, GlobalDeliverableData
from crawler import Frontier
import gc
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier: Frontier, global_deliverable: GlobalDeliverableData):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.logger.info(f"Starting worker {worker_id}...")
        self.worker_id = worker_id
        self.config = config
        self.frontier = frontier

        self.global_deliverable = global_deliverable

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {
            "from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import",
                                                         "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"

        super().__init__(daemon=True)

    def run(self):
        try:
            num_url_processed = 0
            while True:
                tbd_url = self.frontier.get_tbd_url()
                if tbd_url is None:
                    if self.frontier.empty():
                        self.logger.info(
                            "Frontier is empty. Stopping Crawler.")
                        break
                    else:
                        self.logger.info(
                            "Respecting politeness delay since there are no free links to download. Idling Crawler.")
                        time.sleep(self.config.time_delay)
                else:
                    self.logger.info(f"Fetching {tbd_url}")
                    resp = download(tbd_url, self.config, self.logger)
                    # self.logger.info(
                    #     f"Downloaded {tbd_url}, status <{resp.status}>, "
                    #     f"using cache {self.config.cache_server}.")
                    num_url_processed += 1

                    scraped_urls = scraper.scraper(
                        tbd_url, resp, self.global_deliverable)

                    for scraped_url in scraped_urls:
                        self.frontier.add_url(scraped_url)

                    self.frontier.mark_url_complete(tbd_url)

                    # hail mary garbage collection so hopefully Linux stops killing my processes
                    del resp
                    del scraped_urls
                    if num_url_processed % 20 == 0:
                        gc.collect()

                    time.sleep(self.config.time_delay)

            self.logger.info(f"Worker {self.worker_id} shutting down.")
        except Exception as e:
            self.logger.exception(
                f"Worker {self.worker_id} encountered a critical error: {e}")
            raise e
