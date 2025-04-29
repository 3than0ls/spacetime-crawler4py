from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import words


with open("./deliverables/stopwords.txt", "r") as f:
    _STOPWORDS = set(f.read().split())
assert len(
    _STOPWORDS) > 0, "Stopwords not found or appear to not be processed correctly."


_WORDS = set(words.words())


def extract_text(soup: BeautifulSoup) -> str:
    """
    Takes a bs4 BeautifulSoup and returns a text containing filtered and stripped text from the soup.
    """
    text = soup.get_text(separator=" ", strip=True)


def _tokenize(text: str) -> Counter:
    """
    ADAPTED FROM ASSIGNMENT 1
    Returns a Counter object representing the count of all tokens.
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
            if buffer:
                tokens[buffer] += 1
                buffer = ""
        cursor += 1

    # append anything leftover in the buffer
    if buffer:
        tokens[buffer] += 1

    return tokens


def get_words(text: str) -> Counter:
    """
    Returns a Counter object representing the count of all words.
    Typically this text is extracted from a BeautifulSoup via get_text().
    """
    tokens = _tokenize(text)
    words = Counter({
        token: count for token, count in tokens.items()
        if token in _WORDS and token not in _STOPWORDS and len(token) > 1
    })
    return words
