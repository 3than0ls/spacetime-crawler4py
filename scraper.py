import re
from urllib.parse import urlparse
from utils.response import Response
from utils import get_logger
from datetime import datetime
from bs4 import BeautifulSoup
import json

timestamp = datetime.now().strftime("%m-%d-%H:%M:%S")
log = get_logger("CUSTOM", f"LOG-{timestamp}")

# https://canvas.eee.uci.edu/courses/72511/assignments/1584020


def scraper(url, resp) -> list[str]:
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
        log.error(
            f"Response raw response: {json.dumps(resp.raw_response)}")
        return links

    if resp.raw_response is None and (res.raw_response.url is not None and res.raw_response.content is not None):
        log.error(
            f"Response returned a 200 code, yet had no raw response. Object is {res.raw_response} Skipping...")
        return links

    if resp.raw_response:
        log.info(f"Extracting links from {resp.raw_response.url}")
        log.info(f"Link contents length:{len(resp.raw_response.content)}")
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        all_links = soup.find_all("a", href=True)
        links = [a_tag['href']
                 for a_tag in all_links if is_valid(a_tag['href'])]
        log.info(
            f"Found {len(links)} valid links (out of {len(all_links)} total links) in the response content")

    return links


VALID_DOMAINS = set([
    "ics.uci.edu",
    "cs.uci.edu",
    "informatics.uci.edu",
    "stat.uci.edu",
])

FORBIDDEN_QUERIES = set(
    ["action=login",
     "action=download",
     "action=upload",
     "action=edit",
     "action=search",
     "action=source",
     "share="
     ])


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

        if not parsed.scheme in set(["http", "https"]):
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
        if any((BAD_QUERY in parsed.query) for BAD_QUERY in FORBIDDEN_QUERIES):
            return False

        # filter only domain specific
        if not (
            any(
                (domain.endswith(f".{VALID_DOMAIN}")
                 or domain == VALID_DOMAIN)
                for VALID_DOMAIN in VALID_DOMAINS
            ) or (
                domain == "today.uci.edu"
                and path.startswith("/department/information_computer_sciences/"))
        ):
            return False

        # alright... manually going through the robots.txt for the
        # https://ics.uci.edu/robots.txt and https://cs.ics.uci.edu/robots.txt
        # Disallow: /people
        # Disallow: /happening
        if (domain == "ics.uci.edu" or domain == "www.ics.uci.edu" or
                domain == "cs.uci.edu" or domain == "www.cs.uci.edu") \
                and (path.startswith("/people") or path.startswith("/happening")):
            return False

        # https://www.informatics.uci.edu/robots.txt and https://www.stat.uci.edu/robots.txt
        # Disallow: /wp-admin/ but allow /wp-admin/admin-ajax.php
        if (domain == "informatics.uci.edu" or domain == "www.informatics.uci.edu" or
                domain == "stat.uci.edu" or domain == "www.stat.uci.edu") \
                and (path.startswith("/wp-admin") and not path.startswith("/wp-admin/admin-ajax")):
            return False
        # Disallow: /research/ (informatics only)
        if (domain == "informatics.uci.edu" or domain == "www.informatics.uci.edu") \
                and path.startswith("/research"):
            return False

        # avoid calendar traps by avoiding paths that look like they contain a calendar
        # anything that looks like a calendar is probably evil
        path_parts = parsed.path.split("/")
        if any(
            re.search(
                r"(?:\d{2}|\d{4})\D+\d{1,2}\D+\d{1,2}|"
                + r"\d{1,2}\D+\d{1,2}\D+(?:\d{2}|\d{4})|"
                + r"(?:\d{2}|\d{4})\D+\d{1,2}|"
                + r"\d{1,2}\D+(?:\d{2}|\d{4})", path_part)
            for path_part in [*path_parts, parsed.path]
        ):
            return False

        return True

    except TypeError:
        print("TypeError for ", parsed)
        raise
