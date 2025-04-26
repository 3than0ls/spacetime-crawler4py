import re
from urllib.parse import urlparse
from utils.response import Response
from utils import get_logger
from datetime import datetime
from bs4 import BeautifulSoup
import json
from deliverables import Deliverable, process_page
from validate import VALID_SCHEMES, VALID_DOMAINS, INVALID_DOMAINS, INVALID_PATHS, INVALID_FRAGMENTS, INVALID_QUERIES

timestamp = datetime.now().strftime("%m-%d:%H:%M:%S")
log = get_logger("CUSTOM", f"LOG-{timestamp}")

# https://canvas.eee.uci.edu/courses/72511/assignments/1584020


def scraper(url, resp: Response, deliverable: Deliverable) -> list[str]:
    # psuedo: if response is invalid, return an empty list (currently done in extract_next_links)
    # pseudo: soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    # deliverable |= process_page(response_url, soup)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp: Response) -> list[str]:
    """
    I would much rather call this function "process_response" and still have it return a list with the hyperlinks

    url: the URL that was used to get the page
    resp.url: the actual url of the page
    resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    resp.error: when status is not 200, you can check the error here, if needed.
    resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
            resp.raw_response.url: the url, again
            resp.raw_response.content: the content of the page!
    Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    """

    links = []

    if not resp.status == 200:
        log.error(
            f"Response error status: {resp.status} - from fetched for {url}, acquired from {resp.url}")
        log.error(f"Response error data: {resp.status}")
        if resp.raw_response is not None:
            log.error(
                f"Response raw response: {resp.raw_response.content}")
        return links

    # essentially a type check to ensure these all exist
    if resp.raw_response is None or resp.raw_response.url is None or resp.raw_response.content is None:
        log.error(
            f"Response returned a 200 code, yet had no raw response.")
        return links

    if resp.raw_response:
        log.info(
            f"Processing page fetched for {url}, acquired from {resp.url}")
        log.info(f"Page contents length: {len(resp.raw_response.content)}")
        content_length = len(resp.raw_response.content)

        if url != resp.url:
            log.warning(
                f"Fetched URL was not an exact match with response URL ({url} and {resp.url})")
        if url not in resp.url:
            log.warning(
                f"Fetched URL was not near match with response URL ({url} and {resp.url})")

        if content_length < 100:
            log.warning(
                f"{resp.url} contents contain little information, despite returning 200.")
            log.warning(f"{resp.url} contents: {resp.raw_response}")

        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        all_links = soup.find_all("a", href=True)
        links = [a_tag['href']
                 for a_tag in all_links if is_valid(a_tag['href'])]
        # log.info(
        #     f"Found {len(links)} valid links (out of {len(all_links)} total links) in the response content")

    return links


def is_valid(url):
    """
    Decide whether to crawl this url or not.
    If you decide to crawl it, return True; otherwise return False.
    There are already some conditions that return False.
    """
    try:
        parsed = urlparse(url)

        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        if not parsed.scheme in VALID_SCHEMES:
            return False

        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", path
        ):
            return False

        # caused frequently by sli.ics.uci.edu; typically has too many redirections
        # bad queries typically lead to a 4XX error, which glean no information anyway
        if any((invalid_query in parsed.query) for invalid_query in INVALID_QUERIES):
            return False

        # filter only domain specific; avoid stepping out of boundaries
        if not (
            any(
                (domain.endswith(f".{valid_domain}")
                 or domain == valid_domain)
                for valid_domain in VALID_DOMAINS
            ) or (
                domain == "today.uci.edu"
                and path.startswith("/department/information_computer_sciences/"))
        ):
            return False

        # some websites have a robots.txt that explicitly state Disallow: /
        # these sites return a 608 from cache server if attempted to be downloaded
        if domain in INVALID_DOMAINS:
            return False

        for _domain, invalid_paths in INVALID_PATHS.items():
            if (domain == _domain or domain == f"www.{_domain}") \
                    and any(path.startswith(invalid_path) for invalid_path in invalid_paths):
                return False

        # avoid calendar traps by avoiding paths that look like they contain a calendar
        # anything that looks like a calendar is probably evil
        path_parts = parsed.path.split("/")
        query_parts = parsed.query.split("&")
        if any(
            re.search(
                r"(?:\d{2}|\d{4})\D+\d{1,2}\D+\d{1,2}|"
                + r"\d{1,2}\D+\d{1,2}\D+(?:\d{2}|\d{4})|"
                + r"(?:\d{2}|\d{4})\D+\d{1,2}|"
                + r"\d{1,2}\D+(?:\d{2}|\d{4})", path_part)
            for path_part in [*path_parts, *query_parts, parsed.path]
        ):
            return False

        if any((invalid_fragment in parsed.fragment) for invalid_fragment in INVALID_FRAGMENTS):
            return False

        return True

    except TypeError:
        print("TypeError for ", parsed)
        raise
