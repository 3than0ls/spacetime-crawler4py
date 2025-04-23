import unittest

from scraper import is_valid

class TestIsValid(unittest.TestCase):
    def test_scheme(self):
        self.assertFalse(is_valid("bad://xxx.com"))
        self.assertFalse(is_valid("bad://www.xxx.com"))
        self.assertTrue(is_valid("https://www.ics.uci.edu/"))
        self.assertFalse(is_valid("foo://bar.baz.stat.uci.edu/foo/bar#baz"))

    def test_bad_fileext(self):
        self.assertTrue(is_valid("http://www.ics.uci.edu/foo.txt"))
        self.assertFalse(is_valid("http://cs.uci.edu/foo.css"))
        self.assertFalse(is_valid("http://today.uci.edu/department/information_computer_sciences/foo/bar/baz.jpg"))

    def test_valid_domains(self):
        self.assertTrue(is_valid("https://ics.uci.edu/"))
        self.assertTrue(is_valid("http://hub.ics.uci.edu/"))
        self.assertTrue(is_valid("https://foo.cs.uci.edu/bar"))
        self.assertTrue(is_valid("http://research.informatics.uci.edu/foo"))
        self.assertTrue(is_valid("https://today.uci.edu/department/information_computer_sciences/foo/bar/baz"))

    def test_invalid_domains(self):
        self.assertTrue(is_valid("https://ics.uci.edu"))
        self.assertFalse(is_valid("http://foo.com/"))
        self.assertFalse(is_valid("https://engineering.uci.edu/"))
        self.assertFalse(is_valid("https://google.com"))
        self.assertFalse(is_valid("http://ics.uci.edu.evil.com/"))
        self.assertFalse(is_valid("https://today.uci.edu/department/engineering/"))
        self.assertFalse(is_valid("http://math.uci.edu/"))
        self.assertFalse(is_valid("http://uci.edu/"))
        self.assertFalse(is_valid("https://cnn.com"))


if __name__ == '__main__':
    unittest.main()