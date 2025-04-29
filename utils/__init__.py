import os
import logging
from hashlib import sha256
from urllib.parse import urlparse, urlunparse


def get_logger(name, filename=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if os.getenv("TESTING") == "true":
        return logger

    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    fh = logging.FileHandler(f"Logs/{filename if filename else name}.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_urlhash(url):
    parsed = urlparse(url)
    # everything other than scheme.
    return sha256(
        f"{parsed.netloc}/{parsed.path}/{parsed.params}/"
        f"{parsed.query}/{parsed.fragment}".encode("utf-8")).hexdigest()


def normalize(url):
    if url.endswith("/"):
        return url.rstrip("/")
    # if "www." in url:
    #     url = url.replace("www.", "", 1)
    return url


def get_domain_name(url: str):
    parsed = urlparse(url)
    if not parsed.netloc:
        return url.replace("www.", "", 1)
    else:
        return parsed.netloc.replace("www.", "", 1)


# im tired of testing
assert get_domain_name(
    "https://www.ics.uci.edu") == "ics.uci.edu", get_domain_name(
    "https://www.ics.uci.edu")
assert get_domain_name("www.cs.uci.edu") == "cs.uci.edu"
