from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from deliverables import GlobalDeliverableData


class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory

        self.global_deliverables = GlobalDeliverableData()

    def start_async(self):
        self.logger.info(f"Creating {self.config.threads_count} workers")
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.global_deliverables)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.logger.info(f"Starting crawler")
        self.start_async()
        self.join()
        self.logger.info(f"Finished crawl, outputting deliverables.")
        self.finish()
        self.logger.info(f"Finished program.")

    def join(self):
        for worker in self.workers:
            worker.join()

    def finish(self):
        self.global_deliverables.mark_finished()
        self.global_deliverables.output()
