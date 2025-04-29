import unittest
from bs4 import BeautifulSoup
from scraper import extract_next_links
from utils.response import Response


class TestExtractNextLinks(unittest.TestCase):
    def test_soup(self):
        with open("./unittests/test.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')
        hrefs = soup.find_all('a')
        self.assertEqual(len(hrefs), 7)

        text = soup.get_text(separator=' ')
        self.assertNotIn('<a>', text)

    def test_scraper(self):
        with open("./unittests/test.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, "html.parser")
        out = extract_next_links("test.html", soup)

        self.assertEqual(len(out), 4)
        self.assertNotIn("https://cnn.com", out)

    def test_extract_absolute_relative_links(self):
        with open("./unittests/test2.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, "html.parser")
        out = extract_next_links("https://ics.uci.edu", soup)
        self.assertIn("https://ics.uci.edu", out)
        self.assertIn("https://ics.uci.edu/foo", out)
        self.assertNotIn("/foo", out)


if __name__ == '__main__':
    unittest.main()
