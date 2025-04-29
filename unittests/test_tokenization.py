import unittest
from bs4 import BeautifulSoup
from deliverables.tokenization import _tokenize, get_words
from utils.response import Response


class TestTokenization(unittest.TestCase):
    def test_tokenize_words(self):
        text = " ".join((*(["foo"]*15), *(["bar"]*10), *(["baz"]*25)))

        words = _tokenize(text)

        self.assertEqual(words['foo'], 15)
        self.assertEqual(words['bar'], 10)
        self.assertEqual(words['baz'], 25)

    def test_tokenize_file_foo(self):
        with open("./unittests/test_foo.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        words = _tokenize(text)

        self.assertEqual(words['foo'], 115)
        self.assertEqual(words['baz'], 1)

    def test_tokenize_file_bar(self):
        with open("./unittests/test_bar.html", 'r') as f:
            text = f.read()

        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        words = _tokenize(text)

        self.assertEqual(words['bar'], 116)
        self.assertEqual(words['baz'], 1)

    def test_get_words(self):
        words = get_words("one two two hello world qwerty uiop a 1")
        self.assertEqual(words['one'], 1)
        self.assertEqual(words['two'], 2)
        self.assertEqual(words['hello'], 1)
        self.assertEqual(words['world'], 1)
        self.assertEqual(words['qwerty'], 0)
        self.assertEqual(words['a'], 0)
        self.assertEqual(words['1'], 0)


if __name__ == '__main__':
    unittest.main()
