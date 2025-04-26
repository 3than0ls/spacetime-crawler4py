import unittest
from bs4 import BeautifulSoup
from deliverables import process_page, finalize
from utils.response import Response


class TestExtractNextLinks(unittest.TestCase):
    def test_process_page(self):
        with open("./unittests/test.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')

        process_page("https://ics.uci.edu/notreal#fake", soup)

    def test_finalize(self):
        pass


if __name__ == '__main__':
    unittest.main()
