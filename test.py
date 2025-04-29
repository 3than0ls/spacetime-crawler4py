import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Step 1: Define base URL and fetch the page
base_url = "https://swiki.ics.uci.edu/doku.php"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Extract and resolve all href links
parsed_links = []

for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    full_url = urljoin(base_url, href)  # resolve relative URLs
    parsed = urlparse(full_url)
    parsed_links.append(parsed)

# Step 3: Sort the links alphabetically by the full URL string
parsed_links.sort(key=lambda p: p.geturl().lower())

# Step 4: Print parsed components
for p in parsed_links:
    print(p.geturl())

print(urljoin("https://swiki.ics.uci.edu/doku.php", "/foo"))
print(urljoin("https://swiki.ics.uci.edu/doku.php",
      "https://swiki.ics.uci.edu/doku.php/foo"))
print(urljoin("https://swiki.ics.uci.edu/doku.php",
      "https://ics.uci.edu/foo"))

# need to test relative links
