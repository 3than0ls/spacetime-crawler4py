"""
This file contains all constants pertaining to the is_valid function in scraper.py

Any schemes, domains, queries, fragments, etc. that would make a URL valid or invalid are stored here.
"""

VALID_SCHEMES = set(["http", "https"])

# the crawl parameters; do not crawl past these
# does not include today.uci.edu/department/information_computer_sciences which is unfortunately hardcoded
VALID_DOMAINS = set([
    "ics.uci.edu",
    "cs.uci.edu",
    "informatics.uci.edu",
    "stat.uci.edu",
])

# means that the robots.txt file found at the root disallows all
INVALID_DOMAINS = set([
    "intranet.ics.uci.edu"
])

# handling invalid paths is contingent on the authorities' robots.txt
# thus must be handled differently; there is no "one set fits all"
# these data and information was noticed to return a 608 during crawling, and found in robots.txt to be disallowed
INVALID_PATHS = {
    "ics.uci.edu": set(["/people", "/happening"]),
    "cs.uci.edu": set(["/people", "/happening"]),
    # informatics and stat also have a path /wp-admin/admin-ajax.php that falls under /wp-admin,
    # and while it's valid, it contains literally zero data except a 0.
    "informatics.uci.edu": set(["/wp-admin", "/research"]),
    "stat.uci.edu": set(["/wp-admin"]),
    # randomly found robots.txt says for this website:
    "www-db.ics.uci.edu": set(["/cgi-bin", "/web-images", "/downloads", "/glimpse_index", "/pages/internal"]),
    # not actually disallowed, but this guy publishes a lot of blogs, and then has a bunch of tags for each blog
    # each tag doesn't actually produce new content; several tags point to the same content
    "ngs.ics.uci.edu": set(["/tag"])
}

# paths that include these segments should be skipped
INVALID_PATH_SEGMENTS = set([
    "files/pdf",
    "file/pdf"
])


INVALID_QUERIES = set([
    # these queries are associated with actions that do not produce a webpage
    "action=login",
    "action=download",
    "action=upload",
    "action=edit",
    "action=search",
    "action=source",
    "share=",
    # these queries are associated with calendar actions that do not produce a webpage
    "ical=",
    "outlook=",
    "outlook-ical=",
    # redirect to is never a good query
    "redirect_to="
])

# these fragments are associated with links that produce the exact same page, but pointing to a different section
# they are the first line of defense against the fragment issue; that is
# links with different fragments producing identical pages (because the domain and path are same)
# UPDATE: design choice was made to ignore fragment when considering URLs
# thus the same URL but with different fragments is treated as the same URL
# rendering this as a minor optimization in the is_valid function, rather than anything useful
INVALID_FRAGMENTS = set([
    "comment-",
    "respond"
])
