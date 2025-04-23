import unittest
from bs4 import BeautifulSoup
from scraper import extract_next_links
from utils.response import Response


class TestExtractNextLinks(unittest.TestCase):
    def test_soup(self):
        with open("./unittests/Wikipedia.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')
        hrefs = soup.find_all('a')
        self.assertEqual(len(hrefs), 370)

    def test_extract_wikipedia(self):
        with open("./unittests/Wikipedia.html", 'r') as f:
            text = f.read()

        resp = Response({
            "url": "x",
            "status": 200,
        })
        resp.raw_response = {
            "url": "raw_x",
            "content": text
        }

        out = extract_next_links("x", resp)

        self.assertEqual(len(out), 0)

    def test_scraper_custom(self):
        with open("./unittests/custom.html", 'r') as f:
            text = f.read()

        resp = Response({
            "url": "x",
            "status": 200,
        })
        resp.raw_response = {
            "url": "raw_x",
            "content": text
        }

        out = extract_next_links("x", resp)

        self.assertEqual(len(out), 5)
        self.assertNotIn("https://cnn.com", out)


if __name__ == '__main__':
    unittest.main()
