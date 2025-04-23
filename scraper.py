import re
from urllib.parse import urlparse
from utils.response import Response
from utils import get_logger
from datetime import datetime
from bs4 import BeautifulSoup

timestamp = datetime.now().strftime("%m-%d-%H:%M:%S")
log = get_logger("CUSTOM", f"LOG-{timestamp}")

# https://canvas.eee.uci.edu/courses/72511/assignments/1584020


def scraper(url, resp) -> list[str]:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp: Response) -> list[str]:
    """
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
            f"Response error status: {resp.error}\nError message: {resp.raw_response.content}")
        return links

    if resp.raw_response is None:
        log.error(
            f"Response returned a 200 code, yet had no raw response. Skipping...")
        return links

    if resp.raw_response:
        log.info(f"Extracting links from {resp.raw_response["url"]}")
        log.info(f"Link contents length:\n{len(resp.raw_response["content"])}")
        soup = BeautifulSoup(resp.raw_response["content"], "html.parser")
        all_links = soup.find_all("a", href=True)
        links = [a_tag['href']
                 for a_tag in all_links if is_valid(a_tag['href'])]
        log.info(
            f"Found {len(links)} valid links (out of {len(all_links)} total links) in the response content")

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

        if not (
            domain.endswith("ics.uci.edu")
            or domain.endswith("cs.uci.edu")
            or domain.endswith("informatics.uci.edu")
            or domain.endswith("stat.uci.edu")
            or (
                domain == "today.uci.edu"
                and path.startswith("/department/information_computer_sciences/")
            )
        ):
            return False

        return True

    except TypeError:
        print("TypeError for ", parsed)
        raise
