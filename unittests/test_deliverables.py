import unittest
from bs4 import BeautifulSoup
from deliverables import process_page, finalize, Deliverable
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

        # TODO: ALL OF THE BELOW NEED TO BE IMPLEMENTED
        self.assertEqual(deliverable.words['foo'], 15)
        self.assertEqual(deliverable.longest_page_len, 0)
        self.assertEqual(len(deliverable.words), 17)

    def test_accumulate_deliverable(self):
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


if __name__ == '__main__':
    unittest.main()
