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
from collections import Counter
from utils import get_logger
from urllib.parse import urlparse, urlunparse


timestamp = datetime.now().strftime("%m-%d-%H:%M:%S")
log = get_logger("DELIVERABLE", f"DELIVERABLE-{timestamp}")


class Deliverable:
    """
    Responsible for managing the data used in the project deliverable for one worker. 
    When single threaded, this object represents the deliverables for the entire crawl.
    When multithreaded, the deliverables must be merged together before producing the final deliverable data.
    """

    def __init__(self, deliverable_id=None):
        self.deliverable_id = deliverable_id

        # self explanatory data representing deliverable objectives
        self.unique_urls = set()

        # for the page with longest length
        self.longest_page_len = 0
        self.longest_page_url = None

        # for the 50 most common words
        self.words = Counter()

        # for the count of subdomains
        self.subdomains = Counter()

    def __or__(self, other: "Deliverable") -> "Deliverable":
        raise NotImplementedError("Use ior (the |=) operator instead.")

    def __ior__(self, other: "Deliverable") -> None:
        """
        Merge two deliverables! Just a neat way to do this.
        Used in the accumulate function below, and to "join" the worker's deliverable with process_page's output.
        Almost doing too much.
        """
        self.unique_urls |= other.unique_urls
        if other.longest_page_len >= self.longest_page_len:
            self.longest_page_len = other.longest_page_len
            self.longest_page_url = other.longest_page_url
        self.words += other.words
        self.subdomains += other.subdomains
        return self

    @classmethod
    def accumulate(cls, deliverables: list["Deliverable"]) -> "Deliverable":
        """
        For multithreading purposes; but can be used if len(deliverables) is 1 too (single threaded).
        Accumulates the values in the deliverables to produce one new final deliverable.
        """
        log.info(
            f"Accumulating {len(deliverables)} into a single deliverable object.")
        accumulated = Deliverable("--FINAL--")

        for deliverable in deliverables:
            accumulated |= deliverable

        return accumulated


def process_page(response_url: str, response_soup: BeautifulSoup) -> Deliverable:
    """
    Process a response's url and content (in the form of bs4 BeautifulSoup) to help answer deliverable questions.
    Returns a deliverable representing the data gleaned from the url/page/soup.
    """
    deliverable = Deliverable(response_url)
    try:
        parsed = urlparse(response_url)
        log.info(f"Processing page {parsed.geturl()}")

        # DELIVERABLE: UNIQUE PAGES
        unique_url = urlunparse([
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''
        ])
        deliverable.unique_urls.add(unique_url)

        # DELIVERABLE: LONGEST PAGE
        # words are tokens that have HTML tags filtered out;
        # whether or not we define tokens to already not include HTMl tags is TBD
        words = Counter()
        num_words = sum(words.values())
        if num_words >= deliverable.longest_page_len:
            deliverable.longest_page_url = response_url

        deliverable.words += words

        # DELIVERABLE: MOST COMMON WORDS
        # all valid links end with .uci.edu anyway, but
        assert "uci.edu" in parsed.netloc, f"Somehow processing {response_url}, despite it not being a valid URL."
        deliverable.subdomains[parsed.netloc] += 1

    except TypeError as e:
        log.error(e)
        raise e

    return deliverable


def finalize(fname=None):
    if fname is None:
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
