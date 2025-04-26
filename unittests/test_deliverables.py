import unittest
from bs4 import BeautifulSoup
from deliverables import process_page, Deliverable
from utils.response import Response
from collections import Counter


class TestExtractNextLinks(unittest.TestCase):
    def test_process_page(self):
        with open("./unittests/test.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')

        deliverable = Deliverable()
        deliverable |= process_page("https://ics.uci.edu/notreal#fake", soup)

        self.assertTrue(
            "https://ics.uci.edu/notreal" in deliverable.unique_urls)
        self.assertTrue("ics.uci.edu" in deliverable.subdomains)
        self.assertEqual(len(deliverable.subdomains), 1)
        self.assertEqual(deliverable.longest_page_url,
                         "https://ics.uci.edu/notreal#fake")

        self.assertEqual(deliverable.words['foo'], 4)
        self.assertEqual(deliverable.longest_page_len, 52)
        self.assertEqual(len(deliverable.words), 14)

    def test_accumuluate_deliverable(self):
        A = Deliverable("A")
        A.unique_urls = set(["xxx", "yyy", "xxx/abc", "yyy/abc/?def"])
        A.longest_page_len = 500
        A.longest_page_url = "xxx"
        A.words = Counter(hello=20, world=20)
        A.subdomains = Counter(xxx=2, yyy=2)
        B = Deliverable("B")
        A.unique_urls = set(["foo", "bar", "foo/baz", "bar/baz/?idk", "xxx"])
        A.longest_page_len = 1500
        A.longest_page_url = "foo"
        A.words = Counter(world=5, hold=5, on=5)
        A.subdomains = Counter(foo=2, bar=2, xxx=1)
        final = Deliverable.accumulate([A, B])

        self.assertEqual(final.unique_urls, A.unique_urls | B.unique_urls)
        self.assertEqual(final.longest_page_len, 1500)
        self.assertEqual(final.longest_page_url, "foo")
        self.assertEqual(final.words,
                         A.words + B.words)
        self.assertEqual(final.subdomains,
                         A.subdomains + B.subdomains)

    def test_deliverable_multifile(self):
        with open("./unittests/foo.html", 'r') as f:
            foo = f.read()
        with open("./unittests/bar.html", 'r') as f:
            bar = f.read()

        foo_soup = BeautifulSoup(foo, 'html.parser')
        bar_soup = BeautifulSoup(bar, 'html.parser')

        deliverable = Deliverable()
        deliverable |= process_page("https://TEST_FOO.uci.edu", foo_soup)
        deliverable |= process_page(
            "https://TEST_BAR.uci.edu/longer_page#IGNORE_FRAG", bar_soup)

        self.assertEqual(deliverable.longest_page_len, 117)
        self.assertEqual(deliverable.longest_page_url,
                         "https://TEST_BAR.uci.edu/longer_page#IGNORE_FRAG")
        self.assertEqual(deliverable.unique_urls, set(
            ["https://TEST_FOO.uci.edu", "https://TEST_BAR.uci.edu/longer_page"]))
        self.assertEqual(set(deliverable.subdomains.keys()), set(
            ["TEST_FOO.uci.edu", "TEST_BAR.uci.edu"]))
        self.assertEqual(deliverable.words["foo"], 115)
        self.assertEqual(deliverable.words["bar"], 116)
        self.assertEqual(deliverable.words["baz"], 2)

    def test_accumulate_multifile(self):
        with open("./unittests/foo.html", 'r') as f:
            foo = f.read()
        with open("./unittests/bar.html", 'r') as f:
            bar = f.read()

        foo_soup = BeautifulSoup(foo, 'html.parser')
        bar_soup = BeautifulSoup(bar, 'html.parser')

        foo_deliv = Deliverable()
        bar_deliv = Deliverable()
        foo_deliv |= process_page("https://TEST_FOO.uci.edu", foo_soup)
        bar_deliv |= process_page(
            "https://TEST_BAR.uci.edu/longer_page#IGNORE_FRAG", bar_soup)

        deliverable = Deliverable.accumulate([foo_deliv, bar_deliv])

        self.assertEqual(deliverable.longest_page_len, 117)
        self.assertEqual(deliverable.longest_page_url,
                         "https://TEST_BAR.uci.edu/longer_page#IGNORE_FRAG")
        self.assertEqual(deliverable.unique_urls, set(
            ["https://TEST_FOO.uci.edu", "https://TEST_BAR.uci.edu/longer_page"]))
        self.assertEqual(set(deliverable.subdomains.keys()), set(
            ["TEST_FOO.uci.edu", "TEST_BAR.uci.edu"]))
        self.assertEqual(deliverable.words["foo"], 115)
        self.assertEqual(deliverable.words["bar"], 116)
        self.assertEqual(deliverable.words["baz"], 2)

        # deliverable.output()


if __name__ == '__main__':
    unittest.main()
