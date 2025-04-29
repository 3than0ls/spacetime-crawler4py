from bs4 import BeautifulSoup
from collections import Counter

# ADAPTED FROM ASSIGNMENT 1

with open("./deliverables/stopwords.txt", "r") as f:
    _STOPWORDS = f.read().split()
assert len(
    _STOPWORDS) > 0, "Stopwords not found or appear to not be processed correctly."


def extract_text(soup: BeautifulSoup) -> str:
    """
    Takes a bs4 BeautifulSoup and returns a text containing filtered and stripped text from the soup.
    """
    text = soup.get_text(separator=" ", strip=True)


def tokenize(text: str) -> Counter:
    """
    Returns a Counter object representing the count of all words/tokens.
    Typically this text is extracted from a BeautifulSoup via get_text().
    """
    tokens = Counter()

    buffer = ""
    cursor = 0

    while cursor < len(text):
        char = text[cursor]
        if char.isalnum():
            buffer += char.lower()
        else:
            if buffer and buffer not in _STOPWORDS:
                # if the token is only one letter/character, don't count it
                if len(buffer) > 1:
                    tokens[buffer] += 1
                buffer = ""
        cursor += 1

    # append anything leftover in the buffer
    if buffer and buffer not in _STOPWORDS:
        tokens[buffer] += 1

    return tokens
