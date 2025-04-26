import unittest
from bs4 import BeautifulSoup
from deliverables import tokenize
from utils.response import Response


class TestTokenization(unittest.TestCase):
    def test_tokenize_words(self):
        text = " ".join((*(["foo"]*15), *(["bar"]*10), *(["baz"]*25)))

        words = tokenize(text)

        self.assertEqual(words['foo'], 15)
        self.assertEqual(words['bar'], 10)
        self.assertEqual(words['baz'], 25)

    def test_tokenize_file_foo(self):
        with open("./unittests/foo.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        words = tokenize(text)

        self.assertEqual(words['foo'], 115)
        self.assertEqual(words['baz'], 1)

    def test_tokenize_file_bar(self):
        with open("./unittests/bar.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        words = tokenize(text)

        self.assertEqual(words['bar'], 116)
        self.assertEqual(words['baz'], 1)


if __name__ == '__main__':
    unittest.main()
