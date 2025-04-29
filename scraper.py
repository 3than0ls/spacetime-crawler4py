import re
from urllib.parse import urlparse, urldefrag
from utils.response import Response
from utils import get_logger
from datetime import datetime
from bs4 import BeautifulSoup
import json
from deliverables import Deliverable, process_page
from validate import VALID_SCHEMES, VALID_DOMAINS, INVALID_DOMAINS, INVALID_PATHS, INVALID_FRAGMENTS, INVALID_QUERIES, INVALID_PATH_SEGMENTS

log = get_logger("SCRAPER", f"CRAWLER")

# https://canvas.eee.uci.edu/courses/72511/assignments/1584020


def scraper(url, resp: Response, deliverable: Deliverable) -> list[str]:
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


    This was changed from the original intention for scraper.
    The previous version simply combined extract_next_links with is_valid to produce a list of valid URLs to crawl.
    Now, we use it to validate a response (returning no new links if it is invalid), convert it into bs4 soup, then process soup, then extract next links from soup
    """
    links = []

    if not resp.status == 200:
        log.error(
            f"Response error status: {resp.status} - from fetched for {url}, acquired from {resp.url}")
        log.error(f"Response error data: {resp.status}")
        if resp.raw_response is not None:
            # log.error(
            #     f"Response raw response: {resp.raw_response.content}")
            pass
        return links

    # functions both as error handling for 200 status with no raw response, and a type check guarantee
    if resp.raw_response is None or resp.raw_response.url is None or resp.raw_response.content is None:
        log.error(
            f"Response returned a 200 code, yet had no raw response or missing raw URL.")
        return links

    # if we're somehow redirected that is invalid (typically out of domain), return an empty list
    if not is_valid(resp.raw_response.url):
        return links

    # log.info(
    #     f"Processing page fetched for {url}, acquired from {resp.url}")
    # log.info(f"Page contents length: {len(resp.raw_response.content)}")
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
        # log.warning(f"{resp.url} contents: {resp.raw_response}")

    # now that we know the raw response is something vaild, process it into a soup and use it
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    deliverable |= process_page(resp.raw_response.url, soup)
    links = extract_next_links(url, soup)

    return links


def extract_next_links(url, soup: BeautifulSoup) -> list[str]:
    """
    Extracts the next links for the crawler to crawl through.
    Eliminates duplicate links found in the soup.
    URLs with the same URL expect different hashes are considered duplicates.
    """
    all_links = soup.find_all("a", href=True)
    hrefs = [a_tag['href'] for a_tag in all_links]
    # log.info(
    #     f"Found {len(links)} valid links (out of {len(all_links)} total links) in the response content")

    # design choice: URLs with different fragments but the same everything else are essentially duplicates; so we will cut them out
    unique_links = set([urldefrag(url)[0] for url in hrefs])
    valid_links = [link for link in unique_links if is_valid(link)]
    return valid_links


def is_valid(url):
    """
    Decide whether to crawl this url or not.
    If you decide to crawl it, return True; otherwise return False.
    There are already some conditions that return False.

    Rules are based on a long series of trial and error to see what links are good and what aren't,
    As well as how to identify potential traps just based on URL (such as calendar traps)
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
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|ppsx"
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

        # avoid paths that include things like "files/pdf" (one specific example)
        # https://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018
        if any([path_segment in parsed.path for path_segment in INVALID_PATH_SEGMENTS]):
            return False

        # avoid crawler traps (all)
        path_parts = parsed.path.split("/")
        query_parts = parsed.query.split("&")

        # avoid calendar traps by avoiding paths that look like they contain a calendar
        # anything that looks like a calendar is probably evil
        if any(
            re.search(
                r"(?:\d{2}|\d{4})\D+\d{1,2}\D+\d{1,2}|"
                + r"\d{1,2}\D+\d{1,2}\D+(?:\d{2}|\d{4})|"
                + r"(?:\d{2}|\d{4})\D+\d{1,2}|"
                + r"\d{1,2}\D+(?:\d{2}|\d{4})", path_part)
            for path_part in [*path_parts, *query_parts, parsed.path]
        ):
            return False

        # avoid invalid fragments; obsolete since we defragment all links
        if any((invalid_fragment in parsed.fragment) for invalid_fragment in INVALID_FRAGMENTS):
            return False

        # avoid /page/X issues
        processed_path_parts = [part for part in path_parts if part != '']
        # ensure the path /page/X can exist and is being followed
        if len(processed_path_parts) >= 2 \
                and processed_path_parts[-2] == "page" \
                and re.search(r"\d+", processed_path_parts[-1]):
            return False

        return True

    except TypeError:
        log.error("TypeError for ", parsed)
        raise
