"""
Test my changes to the frontier.
"""


import unittest
from bs4 import BeautifulSoup
from utils.response import Response
from crawler import Frontier
from urllib.parse import urlparse
import time
import os
from configparser import ConfigParser
from argparse import ArgumentParser
from utils.server_registration import get_cache_server
from utils.config import Config
from utils import normalize, get_domain_name, get_urlhash
import threading
import io
import random


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
        ics = self.config.seed_urls[0]
        self.assertIn(ics, f._frontier)
        self.assertIn("ics.uci.edu", f._domains_last_accessed)
        self.assertIn(get_urlhash(ics), f._seen_urls)
        self.assertFalse(f.url_downloaded(get_urlhash(ics)))
        self.assertLess(
            f._domains_last_accessed['ics.uci.edu'], time.time())

    def test_extract(self):
        f = Frontier(self.config, True)
        # f._frontier.insert(2, "https://stat.uci.edu/bungus")
        # f._frontier.insert(2, "https://abc.uci.edu/bungus")
        f._frontier.append("https://www.stat.uci.edu/bad")

        one = f.get_tbd_url()
        self.assertEqual(one, "https://www.stat.uci.edu/bad")
        one_domain = get_domain_name(urlparse(one).netloc)
        self.assertEqual(one_domain, "stat.uci.edu")
        self.assertTrue(
            time.time() - f._domains_last_accessed[one_domain] < 0.1)
        self.assertEqual(len(f._frontier), 4)

        two = f.get_tbd_url()
        two_domain = get_domain_name(urlparse(two).netloc)
        self.assertNotEqual(one_domain, two_domain)
        self.assertEqual(two_domain, "informatics.uci.edu")
        self.assertTrue(len(f._frontier) == 3)

        time.sleep(0.5)

        three = f.get_tbd_url()
        three_domain = get_domain_name(urlparse(three).netloc)
        self.assertEqual(three, "https://www.stat.uci.edu")
        self.assertEqual(three_domain, "stat.uci.edu")
        self.assertTrue(len(f._frontier) == 2)

        four = f.get_tbd_url()
        four_domain = get_domain_name(urlparse(four).netloc)
        self.assertEqual(four_domain, "cs.uci.edu")
        self.assertTrue(len(f._frontier) == 1)

        four = f.get_tbd_url()
        four_domain = get_domain_name(urlparse(four).netloc)
        self.assertEqual(four, "https://www.ics.uci.edu")
        self.assertTrue(len(f._frontier) == 0)

        self.assertIsNone(f.get_tbd_url())
        self.assertEqual(len(f._seen_urls), 4)

    def test_single_domain(self):
        f = Frontier(self.config, True)
        lq = [f"https://one.com/{i+1}" for i in range(3)][::-1]
        f._frontier = lq

        one = f.get_tbd_url()
        self.assertEqual(one, "https://one.com/1")
        self.assertEqual(f.get_tbd_url(), None)
        time.sleep(0.2)
        self.assertEqual(f.get_tbd_url(), None)
        time.sleep(0.5)
        self.assertEqual(f.get_tbd_url(), "https://one.com/2")
        time.sleep(0.5)
        self.assertEqual(f.get_tbd_url(), "https://one.com/3")
        self.assertEqual(f.get_tbd_url(), None)
        self.assertEqual(f.get_tbd_url(), None)

    def test_frontier_downloaded(self):
        f = Frontier(self.config, True)
        lq = ["https://www.stat.uci.edu"][::-1]
        f._frontier = lq

        url = f.get_tbd_url()
        domain = get_domain_name(url)
        self.assertEqual(domain, "stat.uci.edu")
        self.assertFalse(f._can_access_domain(domain))
        self.assertEqual(f.get_tbd_url(), None)
        self.assertIn("stat.uci.edu", f._domains_last_accessed.keys())

    def test_simulation(self):
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
        f._frontier = lq[::-1]

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
        f._frontier = lq[::-1]
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
        f._frontier = lq[::-1]
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

    def test_frontier_no_race_conditions(self):
        f = Frontier(self.config, True)
        lq = [
            "https://one.com",
            "https://two.com",
        ] * 2  # * 200
        f._frontier = lq
        num_threads = 4
        threads = [None] * num_threads
        processed_urls = []

        def worker():
            # a simplified copy of the worker code
            while True:
                delay = 0.5 + random.random()
                tbd_url = f.get_tbd_url()
                if not tbd_url:
                    if f.empty():
                        break
                    else:
                        time.sleep(delay)
                        continue
                processed_urls.append(tbd_url)
                time.sleep(delay)

        for i in range(num_threads):
            threads[i] = threading.Thread(target=worker)
            threads[i].start()

        for thread in threads:
            thread.join()

        odds = processed_urls[1::2]

        self.assertTrue(
            all([link in "https://one.com" for link in odds]) or
            all([link in "https://two.com" for link in odds])
        )

    def test_simulation(self):
        f = Frontier(self.config, True)
        f._frontier = []
        f.add_url("https://one.com")
        self.assertIn("https://one.com", f._frontier)
        self.assertIn(get_urlhash("https://one.com"), f._seen_urls)
        self.assertTrue(f.url_seen(get_urlhash("https://one.com")))

        # download url and scrape
        base = f.get_tbd_url()
        self.assertEqual(base, "https://one.com")
        scraped_urls = ["https://one.com/a", "https://one.com/b"]
        for url in scraped_urls:
            f.add_url(url)

        self.assertIn(scraped_urls[0], f._frontier)
        self.assertIn(get_urlhash(scraped_urls[0]), f._seen_urls)
        self.assertTrue(f.url_seen(get_urlhash(scraped_urls[0])))
        self.assertIn(scraped_urls[1], f._frontier)
        self.assertIn(get_urlhash(scraped_urls[1]), f._seen_urls)
        self.assertTrue(f.url_seen(get_urlhash(scraped_urls[1])))
        
        f.mark_url_complete(base)
        self.assertTrue(f.url_seen(get_urlhash(base)))
        self.assertIn(get_urlhash(base), f._seen_urls)
        self.assertTrue(f.url_downloaded(get_urlhash(base)))
        self.assertIsNone(f.get_tbd_url())
        time.sleep(0.5)

        self.assertFalse(f.empty())
        b = f.get_tbd_url()
        self.assertEqual(b, "https://one.com/b")
        f.mark_url_complete(b)
        self.assertIn(get_urlhash("https://one.com/b"), f._seen_urls)
        self.assertTrue(f.url_downloaded(get_urlhash("https://one.com/b")))
        self.assertIsNone(f.get_tbd_url())
        time.sleep(0.5)

        a = f.get_tbd_url()
        self.assertEqual(a, "https://one.com/a")
        f.mark_url_complete(a)
        self.assertIn(get_urlhash("https://one.com/a"), f._seen_urls)
        self.assertIsNone(f.get_tbd_url())
        time.sleep(0.5)

        self.assertIsNone(f.get_tbd_url())

    def test__load_save(self):
        os.environ["TESTING"] = "false"
        import shelve
        save_file_path = os.path.join(self.config.save_file)
        
        # create shelf
        urls = ["https://one.com", "https://two.com/page"]
        f = Frontier(self.config, True)
        f._seen_urls.clear()
        for url in urls:
            f.add_url(url)
        f.mark_url_complete(f.get_tbd_url())
        f._sync_shelf()
        
        f = Frontier(self.config, False)  # loads from tempfile
        self.assertEqual(f._config.save_file, self.config.save_file)
        # f._load_save()

        self.assertEqual(len(f._seen_urls), 2)
        self.assertIn(get_urlhash(urls[0]), f._seen_urls)
        self.assertIn(get_urlhash(urls[0]), f._seen_urls)
        self.assertIn("https://one.com", f._frontier)
        self.assertNotIn("https://two.com/page", f._frontier)
        
        
        self.assertIn("https://one.com", f._frontier)
        self.assertIn(get_urlhash("https://one.com"), f._seen_urls)
        self.assertTrue(f.url_seen(get_urlhash("https://one.com")))
        self.assertFalse(f.url_downloaded(get_urlhash("https://one.com")))

        self.assertNotIn("https://two.com/page", f._frontier)
        self.assertIn(get_urlhash("https://two.com/page"), f._seen_urls)
        self.assertTrue(f.url_seen(get_urlhash("https://two.com/page")))
        self.assertTrue(f.url_downloaded(get_urlhash("https://two.com/page")))

    def test_memload(self):
        return
        print("memload test... this will take a while\n")
        f = Frontier(self.config, True)
        f._frontier = []
        f._domains_last_accessed.clear()
        f._seen_urls.clear()
        f.add_url("https://0.com")
        length = 250000

        for i in range(length):
            f.get_tbd_url()
            link = f"https://{i+1}{'x'*100}.com"
            costly_memory_operation = io.StringIO("A" * 4000000).read() # 4 megabytes
            url_hash = get_urlhash(link)
            f.add_url(link)
            self.assertTrue(f.url_seen(url_hash))
            f.mark_url_complete(link)
            self.assertTrue(f.url_downloaded(url_hash))

        self.assertIsNotNone(f.get_tbd_url())
        self.assertIsNone(f.get_tbd_url())
        self.assertEqual(len(f._frontier), 0)
        self.assertEqual(len(f._seen_urls), length+1)
        self.assertEqual(len(f._can_access_domain), length+1)

    def tearDown(self):
        os.environ["TESTING"] = "true"
        if os.path.exists(self.config.save_file):
            os.remove(self.config.save_file)
        self._delete_temp()


if __name__ == '__main__':
    unittest.main()
