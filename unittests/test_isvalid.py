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
        self.assertFalse(is_valid(
            "http://today.uci.edu/department/information_computer_sciences/foo/bar/baz.jpg"))
        self.assertFalse(is_valid(
            "http://sli.ics.uci.edu/Pubs/Pubs?action=download&upname=nips99.pdf"
        ))
        self.assertFalse(is_valid(
            "http://sli.ics.uci.edu/Pubs/Pubs?action=download&upname=nips99.ps"
        ))

    def test_valid_domains(self):
        self.assertTrue(is_valid("https://ics.uci.edu/"))
        self.assertTrue(is_valid("http://hub.ics.uci.edu/"))
        self.assertTrue(is_valid("https://foo.cs.uci.edu/bar"))
        self.assertTrue(is_valid("http://research.informatics.uci.edu/foo"))
        self.assertTrue(is_valid(
            "https://today.uci.edu/department/information_computer_sciences/foo/bar/baz"))

    def test_invalid_domains(self):
        self.assertTrue(is_valid("https://ics.uci.edu"))
        self.assertFalse(is_valid("http://foo.com/"))
        self.assertFalse(is_valid("https://engineering.uci.edu/"))
        self.assertFalse(is_valid("https://google.com"))
        self.assertFalse(is_valid("http://ics.uci.edu.evil.com/"))
        self.assertFalse(
            is_valid("https://today.uci.edu/department/engineering/"))
        self.assertFalse(is_valid("http://math.uci.edu/"))
        self.assertFalse(is_valid("http://uci.edu/"))
        self.assertFalse(is_valid("https://cnn.com"))
        # newly added one: this should not be!
        self.assertFalse(
            is_valid("http://news.nacs.uci.edu/2009/05/psearch-nacs-and-ics-collaborate"))

    def test_invalid_query(self):
        # always caused by sli.ics.uci.edu
        self.assertFalse(
            is_valid("http://sli.ics.uci.edu/Category/PmWikiDeveloper?action=login"))
        self.assertFalse(
            is_valid("http://sli.ics.uci.edu/PmWiki/Uploads?action=upload&upname=file.doc"))
        self.assertFalse(
            is_valid("http://sli.ics.uci.edu/Pubs/Pubs?action=download&upname=nips99.ps"))
        self.assertFalse(
            is_valid("https://sli.ics.uci.edu/Classes-2008/Classes-2008?action=edit"))
        self.assertFalse(
            is_valid("http://sli.ics.uci.edu/PmWiki/WikiGroup?action=search&q=fmt%3Dgroup"))
        self.assertFalse(
            is_valid("https://sli.ics.uci.edu/Site/Preferences?action=source"))
        self.assertFalse(
            is_valid("https://sli.ics.uci.edu/Classes-2008/Classes-2008?action=edit"))
        self.assertFalse(
            is_valid(
                "https://wics.ics.uci.edu/spring-2021-week-1-wics-first-general-meeting/?share=twitter")
        )
        self.assertFalse(
            is_valid(
                "https://wics.ics.uci.edu/spring-2021-week-1-wics-first-general-meeting/?share=facebook")
        )

    def test_hardcoded_robotstxt(self):
        self.assertFalse(
            is_valid("https://ics.uci.edu/happening/news/page/3")
        )
        self.assertFalse(
            is_valid("https://ics.uci.edu/people/sven-koenig")
        )
        self.assertFalse(
            is_valid("https://www.informatics.uci.edu/research/*")
        )
        self.assertFalse(
            is_valid("https://www.informatics.uci.edu/wp-admin/")
        )
        # should return True since it technically is valid, but literally only contains "0", so we'll disclude it
        # self.assertTrue(
        #     is_valid("https://www.informatics.uci.edu/wp-admin/admin-ajax.php")
        # )
        self.assertFalse(
            is_valid("https://ics.uci.edu/happening/news/page/3")
        )
        self.assertFalse(
            is_valid("https://www.ics.uci.edu/happening/news/page/3")
        )
        self.assertFalse(
            is_valid("https://ics.uci.edu/happening/news/page/3")
        )
        self.assertFalse(is_valid("https://intranet.ics.uci.edu/"))

    def test_avoid_calendar_traps(self):
        self.assertFalse(
            is_valid("https://isg.ics.uci.edu/events/tag/talks/day/2024-11-08")
        )
        self.assertFalse(
            is_valid(
                "https://isg.ics.uci.edu/events/tag/talks/day/2025-02-03/?outlook-ical=1")
        )
        self.assertFalse(
            is_valid(
                "http://wics.ics.uci.edu/events/category/wics-bonding/2021-03/?outlook-ical=1")
        )
        # these are found in the query portion, not the path portion
        self.assertFalse(
            is_valid("https://ics.uci.edu/page/2/?post_type=tribe_events&eventDisplay=day&tribe_events_cat=graduate-programs&eventDate=2025-04-20&ical=1")
        )
        # arbitrary tests
        self.assertFalse(
            is_valid("https://ics.uci.edu/04.24.2025")
        )
        self.assertFalse(
            is_valid("https://ics.uci.edu/2025.04.24")
        )
        self.assertFalse(
            is_valid("https://ics.uci.edu/4.24.25")
        )
        self.assertFalse(
            is_valid("https://ics.uci.edu/4/24/25")
        )
        self.assertFalse(
            is_valid("https://ics.uci.edu/25/24/4")
        )
        self.assertFalse(
            is_valid("https://www.ics.uci.edu/04/24/25")
        )

    def test_avoid_fragments(self):
        self.assertFalse(
            is_valid("https://ngs.ics.uci.edu/becoming-impatient/#comment-3103")
        )


if __name__ == '__main__':
    unittest.main()
