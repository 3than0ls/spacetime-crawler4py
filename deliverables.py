"""
Functions related to answering the deliverables of this project.


https://canvas.eee.uci.edu/courses/72511/assignments/1584020

As a concrete deliverable of this project, besides the code itself, you must submit a report containing answers to the following questions:

1) How many unique pages did you find? 
    Uniqueness for the purposes of this assignment is ONLY established by the URL, but discarding the fragment part. 
    So, for example, http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL. 
2) What is the longest page in terms of the number of words? 
    (HTML markup doesn't count as words)
3) What are the 50 most common words in the entire set of pages crawled under these domains? 
    (Ignore English stop words) Submit the list of common words ordered by frequency.
4) How many subdomains did you find in the uci.edu domain? 
    Submit the list of subdomains ordered alphabetically and the number of unique pages detected in each subdomain. 
    The content of this list should be lines containing subdomain, number, for example:
    vision.ics.uci.edu, 10 (not the actual number here)

"""

from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict
from utils import get_logger
from urllib.parse import urlparse, urlunparse

_UNIQUE_PAGES = set()

_LONGEST_PAGE_LEN = 0
_LONGEST_PAGE_NAME = None

_MOST_COMMON_WORDS = defaultdict(int)

_SUBDOMAINS_MAP = defaultdict(int)


timestamp = datetime.now().strftime("%m-%d-%H:%M:%S")
log = get_logger("DELIVERABLE", f"DELIVERABLE-{timestamp}")


def process_page(response_url: str, response_soup: BeautifulSoup) -> None:
    """
    Process a response's url and content (in the form of bs4 BeautifulSoup) to help answer deliverable questions.
    """
    try:
        parsed = urlparse(response_url)
        log.info(f"Processing page {parsed.geturl}")

        # DELIVERABLE: UNIQUE PAGES
        unique_url = urlunparse([
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''
        ])
        _UNIQUE_PAGES.add(unique_url)

        # DELIVERABLE: LONGEST PAGE
        # words and tokens are the same in this scenario
        words = defaultdict(int)

        # TODO: IMPLEMENT
        for word, amount in words:
            _MOST_COMMON_WORDS[word] += amount

        # DELIVERABLE: MOST COMMON WORDS
        # all valid links end with .uci.edu anyway, but
        assert "uci.edu" in parsed.netloc, f"Somehow processing {response_url}, despite it not being a valid URL."
        _SUBDOMAINS_MAP[parsed.netloc] += 1

    except TypeError as e:
        log.error(e)
        raise


def finalize():
    timestamp = datetime.now().strftime("%m-%d-%H:%M:%S")
    fname = f"deliverables-{timestamp}"
    with open(fname, 'w+') as f:
        f.write("DELIVERABLE: UNIQUE PAGES")
        f.write(len(_UNIQUE_PAGES))

        f.write("DELIVERABLE: LONGEST PAGE")
        f.write(f"PAGE: {_LONGEST_PAGE_NAME}")
        f.write(f"PAGE LENGTH: {_LONGEST_PAGE_LEN}")

        f.write("DELIVERABLE: MOST COMMON WORDS")
        top_words = sorted(_MOST_COMMON_WORDS.items(),
                           key=lambda x: (-x[1], x[0]))[:50]
        for word, freq in top_words:
            f.write(f"{word}:\t{freq}")

        f.write("DELIVERABLE: SUBDOMAINS")
        alphabetic_subdomains = sorted(
            _SUBDOMAINS_MAP.items(), key=lambda x: (x[0], x[1]))
        for subdomain, count in alphabetic_subdomains:
            f.write(f"{subdomain}:\t{count}")
