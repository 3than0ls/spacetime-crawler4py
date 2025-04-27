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
from urllib.parse import urlparse, urldefrag
from deliverables.tokenization import tokenize
import os
import json


timestamp = datetime.now().strftime("%m-%d:%H:%M:%S")
log = get_logger("DELIVERABLE", f"DELIVERABLE-{timestamp}")


_DELIVERABLES_DIRNAME = "Deliverables"


class Deliverable:
    """
    Responsible for managing the data used in the project deliverable for one worker. 
    When single threaded, this object represents the deliverables for the entire crawl.
    When multithreaded, the deliverables must be merged together before producing the final deliverable data.
    """

    def __init__(self, deliverable_id=None):
        self._deliverable_id = deliverable_id
        self._timestamp = datetime.now().strftime("%m-%d:%H:%M:%S")

        # map of URL to content size (in number of tokens)
        # the keys of this provide UNIQUE_URLS
        # the values provide some insightful debugging data
        self.url_token_sizes = dict()  # url: num of tokens

        # for the page with longest length
        self.longest_page_len = 0
        self.longest_page_url = None

        # for the 50 most common words
        self.words = Counter()

        # for the count of subdomains
        self.subdomains = Counter()

    def _create_deliverables_dir(self):
        if not os.path.exists(_DELIVERABLES_DIRNAME):
            os.makedirs(_DELIVERABLES_DIRNAME)

    def _json_dump(self, fname=None):
        if fname is None:
            fname = f"deliverables-{self._timestamp}-dump"

        fname = os.path.join(_DELIVERABLES_DIRNAME, fname)
        self._create_deliverables_dir()

        with open(fname, 'w+') as f:
            json.dump(
                {
                    "url_token_size": self.url_token_sizes,
                    "longest_page": {
                        "len": self.longest_page_len,
                        "url": self.longest_page_url
                    },
                    "words": dict(self.words),
                    "subdomains": dict(self.subdomains)
                }, sort_keys=True
            )

    def output(self, fname=None):
        if fname is None:
            fname = f"deliverables-{self._timestamp}"

        self._create_deliverables_dir()
        fname = os.path.join(_DELIVERABLES_DIRNAME, fname)

        num_unique_urls = len(self.url_token_sizes)
        longest_page = self.longest_page_url
        longest_page_len = self.longest_page_len
        top_words = sorted(self.words.items(),
                           key=lambda x: (-x[1], x[0]))[:50]
        subdomains_count = sorted(
            self.subdomains.items(), key=lambda x: (x[0], x[1]))

        with open(fname, 'w+') as f:
            f.write(f"File name: {fname}\n")
            f.write(f"Deliverable ID: {self._deliverable_id}\n")
            f.write("\n")
            f.write("--- DELIVERABLE 1: NUMBER OF UNIQUE PAGES ---\n")
            f.write(f"UNIQUE PAGES: {num_unique_urls}")
            f.write("\n")
            f.write("--- DELIVERABLE 2: LONGEST PAGE IN WORDS ---\n")
            f.write(f"PAGE: {longest_page}\n")
            f.write(f"PAGE LENGTH: {longest_page_len}\n")
            f.write("\n")
            f.write("--- DELIVERABLE 3: MOST COMMON WORDS ---\n")
            for word, freq in top_words:
                f.write(f"{word}\t{freq}\n")
            f.write("\n")
            f.write("--- DELIVERABLE 4: SUBDOMAINS COUNT ---\n")
            for subdomain, count in subdomains_count:
                f.write(f"{subdomain}\t{count}\n")

        self._json_dump()

    def __or__(self, other: "Deliverable") -> "Deliverable":
        raise NotImplementedError("Use ior (the |=) operator instead.")

    def __ior__(self, other: "Deliverable") -> None:
        """
        Merge two deliverables! Just a neat way to do this.
        Used in the accumulate function below, and to "join" the worker's deliverable with process_page's output.
        Almost doing too much.
        """
        self.url_token_sizes |= other.url_token_sizes
        if other.longest_page_len >= self.longest_page_len:
            self.longest_page_len = other.longest_page_len
            self.longest_page_url = other.longest_page_url
        self.words += other.words
        self.subdomains += other.subdomains
        return self

    @staticmethod
    def accumulate(deliverables: list["Deliverable"]) -> "Deliverable":
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
        log.info(f"Processing page {response_url}")

        page_text = response_soup.get_text(separator=' ', strip=True)
        words = tokenize(page_text)
        num_words = sum(words.values())

        # DELIVERABLE: UNIQUE PAGES
        unique_url = urldefrag(response_url)[0]
        deliverable.url_token_sizes[unique_url] = num_words

        # DELIVERABLE: LONGEST PAGE
        # words are tokens that have HTML tags filtered out;
        # whether or not we define tokens to already not include HTMl tags is TBD
        deliverable.longest_page_url = response_url
        deliverable.longest_page_len = num_words

        # DELIVERABLE: MOST COMMON WORDS
        deliverable.words += words

        # DELIVERABLE: SUBDOMAIN COUNT
        parsed = urlparse(response_url)
        # all valid links end with .uci.edu anyway, but
        assert "uci.edu" in parsed.netloc, f"Somehow processing {response_url}, despite it not being a valid URL."
        deliverable.subdomains[parsed.netloc] += 1

    except TypeError as e:
        log.error(e)
        raise e

    return deliverable
