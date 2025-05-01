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
from collections import Counter
import os
import json
import shelve
import glob
from dataclasses import dataclass, field
from collections import Counter
from urllib.parse import urldefrag, urlparse
from bs4 import BeautifulSoup

from deliverables.tokenization import get_words
from utils import get_logger
from threading import RLock


DELIVERABLES_LOCK = RLock()


@dataclass
class RawDeliverableData:
    """All data stored here is independent of one another; and it is all accumulated into GlobalDeliverableData"""
    url_word_map: dict = field(default_factory=dict)
    total_urls_seen: int = 0
    words: Counter = field(default_factory=Counter)
    subdomains: Counter = field(default_factory=Counter)
    finished: bool = False


log = get_logger("DELIVERABLE", f"CRAWLER")

class GlobalDeliverableData:
    """
    Responsible for managing the data used in the project deliverable. Stores all it's data in a shelf.
    All threads essentially pipe their RawDeliverableData to this, which then saves it into a shelf.
    The program can stop; and as long as the global deliverable data isn't marked as finished, subsequent
    crawler start ups will continue to update this shelf.
    """
    DELIVERABLES_DIRNAME = "Output"  # keep it in current directory

    @staticmethod
    def create_deliverables_dir():
        if not os.path.exists(GlobalDeliverableData.DELIVERABLES_DIRNAME):
            os.makedirs(GlobalDeliverableData.DELIVERABLES_DIRNAME)

    @staticmethod
    def get_previous_deliverable_fname() -> str | None:
        files = [file for file in glob.glob(GlobalDeliverableData.DELIVERABLES_DIRNAME + "/deliverables*.shelve*") if os.path.isfile(file)]
        for file in files:
            with shelve.open(file) as raw_dev_data:
                if not raw_dev_data.get("finished", False):
                    return file
        else:
            return None


    def __init__(self, shelve_name=None):
        if shelve_name is None:
            # get previous shelf
            previous_shelve = GlobalDeliverableData.get_previous_deliverable_fname()
            if previous_shelve is None:
                GlobalDeliverableData.create_deliverables_dir()
                self._shelve_path = f"{GlobalDeliverableData.DELIVERABLES_DIRNAME}/deliverables-{datetime.now().strftime('%m-%d-%H-%M-%S')}.shelve"
            else:
                self._shelve_path = previous_shelve
        else:
            self._shelve_path = shelve_name
        
        with shelve.open(self._shelve_path) as raw_dev_data:
            raw_dev_data.setdefault("url_word_map", {})
            raw_dev_data.setdefault("total_urls_seen", 0)
            raw_dev_data.setdefault("words", Counter())
            raw_dev_data.setdefault("subdomains", Counter())
            raw_dev_data.setdefault("finished", False)

        self._basename = self._shelve_path.split(".shelve")[0]

    
    def get_raw(self) -> RawDeliverableData:
        """Return a read-only version of the deliverable data"""
        with shelve.open(self._shelve_path) as raw_dev_data:
            out = RawDeliverableData(
                url_word_map=raw_dev_data["url_word_map"],
                total_urls_seen=raw_dev_data["total_urls_seen"],
                words=raw_dev_data["words"],
                subdomains=raw_dev_data["subdomains"],
                finished=raw_dev_data["finished"]
            )

        return out

    def mark_finished(self):
        with shelve.open(self._shelve_path) as raw_dev_data:
            raw_dev_data["finished"] = True
            
    def update(self, batch: RawDeliverableData):
        with DELIVERABLES_LOCK:
            with shelve.open(self._shelve_path, writeback=True) as raw_dev_data:
                raw_dev_data["url_word_map"].update(batch.url_word_map)
                raw_dev_data["total_urls_seen"] += batch.total_urls_seen
                raw_dev_data["words"] += batch.words
                raw_dev_data["subdomains"] += batch.subdomains
                raw_dev_data.sync()

    def _json_dump(self):
        """A completed JSON dump of a finished deliverable. Only to be called after output()"""
        json_path = f"{self._basename}-dump.json"
        out = self.get_raw()

        log.info(f"JSON dumped deliverables to file {json_path}")

        with open(json_path, 'w+') as f:
            json.dump(
                {
                    "url_word_map": out.url_word_map,
                    "total_urls_seen": out.total_urls_seen,
                    "words": dict(out.words),
                    "subdomains": dict(out.subdomains)
                }, fp=f, sort_keys=True, indent=4
            )

    def output(self):
        GlobalDeliverableData.create_deliverables_dir()
        log.info(f"Outputting deliverables found in {self._shelve_path}")

        out = self.get_raw()
        num_unique_valid_urls = len(out.url_word_map)
        num_urls_seen = out.total_urls_seen
        longest_page, longest_page_len = Counter(out.url_word_map).most_common(1)[0]
        top_words = out.words.most_common(50)
        subdomains_count = len(out.subdomains)
        sorted_subdomains = sorted(
            out.subdomains.items(), key=lambda x: (x[0], x[1]))

        deliverable_path = f"{self._basename}.txt"
        with open(deliverable_path, 'w+') as f:
            f.write(f"Deliverable path: {deliverable_path}\n")
            f.write(f"Deliverable ID: {self._basename}\n")
            f.write("\n")
            f.write("--- DELIVERABLE 1: NUMBER OF UNIQUE PAGES ---\n")
            f.write(f"UNIQUE PAGES (DOWNLOADED): {num_unique_valid_urls}\n")
            f.write(f"UNIQUE URLS (SEEN): {num_urls_seen}\n")
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
            f.write(f"Raw subdomain count: {subdomains_count}\n")
            f.write("\n")
            f.write(f"Subdomain counts (alphabetically):\n")
            for subdomain, count in sorted_subdomains:
                f.write(f"{subdomain}\t{count}\n")

        log.info(f"Outputted deliverables to file {deliverable_path}")

        self._json_dump()



def process_page(response_url: str, response_soup: BeautifulSoup) -> RawDeliverableData:
    """
    Process a response's url and content (in the form of bs4 BeautifulSoup) to help answer deliverable questions.
    Returns a deliverable representing the data gleaned from the url/page/soup.
    """
    raw_deliverable = RawDeliverableData()
    try:
        # log.info(f"Processing page {response_url}")
        page_text = response_soup.get_text(separator=' ', strip=True)
        words = get_words(page_text)
        num_words = sum(words.values())

        # DELIVERABLE: UNIQUE PAGES [DOWNLOADED] and LONGEST PAGE
        unique_url = urldefrag(response_url)[0]
        raw_deliverable.url_word_map[unique_url] = num_words

        links = response_soup.find_all('a', href=True)
        unique_urls_in_page = set(urldefrag(link['href'])[0] for link in links)
        raw_deliverable.total_urls_seen += len(unique_urls_in_page)

        # DELIVERABLE: MOST COMMON WORDS
        raw_deliverable.words += words

        # DELIVERABLE: SUBDOMAIN COUNT
        parsed = urlparse(response_url)
        # all valid links end with .uci.edu anyway, but
        assert "uci.edu" in parsed.netloc, f"Somehow processing {response_url}, despite it not being a valid URL."
        raw_deliverable.subdomains[parsed.netloc] = 1

    except TypeError as e:
        log.error(e)
        raise e

    return raw_deliverable

