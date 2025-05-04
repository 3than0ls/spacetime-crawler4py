import re
from urllib.parse import urlparse, urldefrag, urljoin
from utils.response import Response
from utils import get_logger, normalize
from bs4 import BeautifulSoup
from deliverables import process_page, GlobalDeliverableData
from validate import VALID_SCHEMES, VALID_DOMAINS, INVALID_DOMAINS, INVALID_PATHS, INVALID_FRAGMENTS, INVALID_QUERIES, INVALID_PATH_SEGMENTS, FILE_EXT_PATTERN, ANY_NUMBER_PATTERN, CALENDAR_TRAP_PATTERN

f_log = get_logger("SCRAPER", f"FRONTIER")
w_log = get_logger("PROCESSED", f"Worker")

# https://canvas.eee.uci.edu/courses/72511/assignments/1584020


def scraper(url, resp: Response, global_deliverable: GlobalDeliverableData) -> list[str]:
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

    # A unique page:
    # - has a 200 status code
    if not resp.status == 200:
        f_log.error(
            f"Response error status <{resp.status}> - from fetched for {url}, acquired from {resp.url}")
        return links

    # - has a non-empty response body
    # functions both as error handling for 200 status with no raw response, and a type check guarantee
    if resp.raw_response is None or resp.raw_response.content is None:
        f_log.error(
            f"Response returned a 200 code, yet had no raw response.")
        return links

    # - has a valid URL
    # if we're somehow redirected that is invalid (typically out of domain), return an empty list
    if not is_valid(resp.url):
        return links

    # log.info(
    #     f"Processing page fetched for {url}, acquired from {resp.url}")
    # log.info(f"Page contents length: {len(resp.raw_response.content)}")

    if url != resp.url:
        f_log.warning(
            f"Fetched URL was not an exact match with response URL ({url} and {resp.url})")
    if url not in resp.url:
        f_log.warning(
            f"Fetched URL was not near match with response URL ({url} and {resp.url})")

    content_length = len(resp.raw_response.content)
    if content_length < 100:
        f_log.warning(
            f"{resp.url} contents contain little information, despite returning 200.")
        # log.warning(f"{resp.url} contents: {resp.raw_response}")

    # now that we know the raw response is something vaild, process it into a soup and use it
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    deliverable_data = process_page(resp.url, soup)
    global_deliverable.update(deliverable_data)

    links = extract_next_links(url, soup)

    # note that the response URL may not be the same as the unique URL; the unique URL is defragmented and then normalized
    w_log.info(
        f"Processed unique page with unique URL {normalize(urldefrag(resp.url)[0])} containing {deliverable_data.words.total()} words.")

    return links


def extract_next_links(url, soup: BeautifulSoup) -> list[str]:
    """
    Extracts the next links for the crawler to crawl through.
    Eliminates duplicate links found in the soup.
    URLs with the same URL expect different hashes are considered duplicates.
    """
    all_links = soup.find_all("a", href=True)
    scraped_links = [urljoin(url, a_tag['href']) for a_tag in all_links]
    # log.info(
    #     f"Found {len(links)} valid links (out of {len(all_links)} total links) in the response content")
    unique_links = set([urldefrag(url)[0] for url in scraped_links])
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

        if FILE_EXT_PATTERN.match(path):
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
        path_parts = [part for part in parsed.path.split("/") if part != '']
        query_parts = parsed.query.split("&")

        # avoid calendar traps by avoiding paths that look like they contain a calendar
        # anything that looks like a calendar is probably evil
        # make an exception in which domain/YYYY/MM/DD/article_name
        if (
            any(
                CALENDAR_TRAP_PATTERN.search(path_part)
                for path_part in [*path_parts, *query_parts, parsed.path]
            ) and
            not (len(path_parts) > 3 and
                 ANY_NUMBER_PATTERN.match(path_parts[-4]) and len(path_parts[-4]) == 4 and
                 ANY_NUMBER_PATTERN.match(path_parts[-3]) and len(path_parts[-3]) == 2 and
                 ANY_NUMBER_PATTERN.match(path_parts[-2]) and len(path_parts[-2]) == 2 and
                 len(path_parts[-1]) > 0)
        ):
            return False

        # avoid invalid fragments; obsolete since we defragment all links
        if any((invalid_fragment in parsed.fragment) for invalid_fragment in INVALID_FRAGMENTS):
            return False

        # # avoid /page/X issues; if X is greater than 500, something is up...
        # ensure the path /page/X can exist and is being followed
        if len(path_parts) >= 2 \
                and path_parts[-2] == "page" \
                and ANY_NUMBER_PATTERN.search(path_parts[-1]) \
                and int(path_parts[-1]) > 500:
            return False

        return True

    except TypeError:
        f_log.error("TypeError for ", parsed)
        raise
