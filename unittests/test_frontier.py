"""
Test my changes to the frontier.
"""


import unittest
from bs4 import BeautifulSoup
from deliverables import tokenize
from utils.response import Response
from crawler import Frontier
from urllib.parse import urlparse
import time
import os
from configparser import ConfigParser
from argparse import ArgumentParser
from utils.server_registration import get_cache_server
from utils.config import Config
from utils import strip_www
import threading


class TestFrontier(unittest.TestCase):
    def _delete_temp(self):
        for ext in ['bak', 'dat', 'dir']:
            fname = self.config.save_file + "." + ext
            if os.path.exists(fname):
                os.remove(fname)

    def setUp(self):
        cparser = ConfigParser()
        cparser.read("./unittests/test.ini")
        config = Config(cparser)
        self.config = config
        self._delete_temp()  # ensure they are deleted
        self.assertEqual(len(self.config.seed_urls), 4)

    def test_seed_correct(self):
        f = Frontier(self.config, True)
        # result = Frontier._load_into_domain(to_be_downloaded)
        seeds = set(self.config.seed_urls)
        self.assertIn("ics.uci.edu", set(f.domains_last_accessed.keys()))
        self.assertLess(
            f.domains_last_accessed['ics.uci.edu'], time.time())

    def test_extract(self):
        f = Frontier(self.config, True)
        f.to_be_downloaded.insert(2, "https://stat.uci.edu/bungus")

        one = f.get_tbd_url()
        self.assertEqual(one, "https://www.stat.uci.edu")
        one_domain = strip_www(urlparse(one).netloc)

        self.assertTrue(
            time.time() - f.domains_last_accessed[one_domain] < 0.1)
        self.assertTrue(len(f.to_be_downloaded) == 4)

        two = f.get_tbd_url()
        two_domain = strip_www(urlparse(two).netloc)
        self.assertNotEqual(one_domain, two_domain)
        self.assertTrue(len(f.to_be_downloaded) == 3)

        three = f.get_tbd_url()
        three_domain = strip_www(urlparse(three).netloc)
        self.assertEqual(three_domain, "cs.uci.edu")
        self.assertTrue(len(f.to_be_downloaded) == 2)

        four = f.get_tbd_url()
        four_domain = strip_www(urlparse(four).netloc)
        self.assertEqual(four_domain, "ics.uci.edu")
        self.assertTrue(len(f.to_be_downloaded) == 1)

        time.sleep(1)
        one_again = f.get_tbd_url()
        one_again_domain = strip_www(urlparse(one_again).netloc)
        self.assertEqual(one_domain, one_again_domain)
        self.assertTrue(len(f.to_be_downloaded) == 0)

    def test_simulation(self):
        pass
        # write a 4 worker test
        # create my own queue
        f = Frontier(self.config, True)
        lq = [
            "https://one.com/a",  # 1
            "https://one.com/b",  # 5
            "https://one.com/c",  # 8
            "https://two.com/a",  # 2
            "https://two.com/b",  # 6
            "https://two.com/c",  # 9
            "https://three.com/a",  # 3
            "https://three.com/b",  # 7
            "https://four.com/b",  # 4
        ]
        # reverse it so sequential ordering makes sense
        f.to_be_downloaded = lq[::-1]

        download_order = [
            [lq[0], lq[1], lq[2]],
            [lq[3], lq[4], lq[5]],
            [lq[6], lq[7], None],
            [lq[8], None, None],
        ]

        for i in range(0, 2):
            # simulate 4 workers
            one = f.get_tbd_url()
            self.assertEqual(one, download_order[0][i])
            two = f.get_tbd_url()
            self.assertEqual(two, download_order[1][i])
            three = f.get_tbd_url()
            self.assertEqual(three, download_order[2][i])
            four = f.get_tbd_url()
            self.assertEqual(four, download_order[3][i])
            time.sleep(0.5)

    def test_four_threads(self):
        f = Frontier(self.config, True)
        lq = [
            "https://one.com/a",  # 1
            "https://one.com/b",  # 5
            "https://one.com/c",  # 8
            "https://two.com/a",  # 2
            "https://two.com/b",  # 6
            "https://two.com/c",  # 9
            "https://three.com/a",  # 3
            "https://three.com/b",  # 7
            "https://four.com/b",  # 4
        ]
        # reverse it so sequential ordering makes sense
        f.to_be_downloaded = lq[::-1]
        processed_urls = []
        num_threads = 4
        threads = [None] * num_threads

        def worker():
            # a simplified copy of the worker code
            while True:
                tbd_url = f.get_tbd_url()
                if not tbd_url:
                    if f.empty():
                        break
                    else:
                        time.sleep(0.5)
                        continue
                processed_urls.append(tbd_url)
                time.sleep(0.5)

        for i in range(num_threads):
            threads[i] = threading.Thread(target=worker)
            threads[i].start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(processed_urls), len(lq))
        ordered = [
            "https://one.com/a",  # 1
            "https://two.com/a",  # 2
            "https://three.com/a",  # 3
            "https://four.com/b",  # 4
            "https://one.com/b",  # 5
            "https://two.com/b",  # 6
            "https://three.com/b",  # 7
            "https://one.com/c",  # 8
            "https://two.com/c",  # 9
        ]

        self.assertEqual(processed_urls, ordered)

    def test_two_threads(self):
        f = Frontier(self.config, True)
        lq = [
            "https://one.com/a",  # 1
            "https://one.com/b",  # 3
            "https://one.com/c",  # 5
            "https://two.com/a",  # 2
            "https://two.com/b",  # 4
            "https://two.com/c",  # 6
            "https://three.com/a",  # 7
            "https://three.com/b",  # 9
            "https://four.com/b",  # 8
        ]
        # reverse it so sequential ordering makes sense
        f.to_be_downloaded = lq[::-1]
        processed_urls = []
        num_threads = 2
        threads = [None] * num_threads

        def worker():
            # a simplified copy of the worker code
            while True:
                tbd_url = f.get_tbd_url()
                if not tbd_url:
                    if f.empty():
                        break
                    else:
                        time.sleep(0.5)
                        continue
                processed_urls.append(tbd_url)
                time.sleep(0.5)

        for i in range(num_threads):
            threads[i] = threading.Thread(target=worker)
            threads[i].start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(processed_urls), len(lq))
        ordered = [
            "https://one.com/a",  # 1
            "https://two.com/a",  # 2
            "https://one.com/b",  # 3
            "https://two.com/b",  # 4
            "https://one.com/c",  # 5
            "https://two.com/c",  # 6
            "https://three.com/a",  # 7
            "https://four.com/b",  # 8
            "https://three.com/b",  # 9
        ]

        self.assertEqual(processed_urls, ordered)

    def tearDown(self):
        self._delete_temp()


if __name__ == '__main__':
    unittest.main()
