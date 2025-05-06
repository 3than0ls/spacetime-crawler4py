"""
This file contains all constants pertaining to the is_valid function in scraper.py

Any schemes, domains, queries, fragments, etc. that would make a URL valid or invalid are stored here.
"""


import re

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
    "intranet.ics.uci.edu",
    "phpmyadmin.ics.uci.edu",
    "labbie.ics.uci.edu",
    "kdd.ics.uci.edu",
    "pastebin.ics.uci.edu",
])

# handling invalid paths is typically contingent on the authorities' robots.txt
# thus must be handled differently; there is no "one set fits all"
# these data and information was noticed to return a 608 during crawling, and found in robots.txt to be disallowed
INVALID_PATHS = {
    "ics.uci.edu": set([
        "/people", "/happening",
        # sadly, professor epstein's photos are contain low textual information, thus are classified as low information value
        # "/~eppstein/pix/",
        # everyything under these two is low information value, since they're just picture slides. the pages themselves are fine though
        # "/~ziv/ooad/classes/",
        # "/~ziv/ooad/intro_to_se/"
    ]),
    "cs.uci.edu": set(["/people", "/happening"]),
    "cs.ics.uci.edu": set(["/people", "/happening"]),
    # informatics and stat also have a path /wp-admin/admin-ajax.php that falls under /wp-admin,
    # and while it's valid, it contains literally zero data except a 0.
    "informatics.uci.edu": set(["/wp-admin", "/research"]),
    "stat.uci.edu": set(["/wp-admin"]),
    # randomly found robots.txt says for this website:
    "www-db.ics.uci.edu": set(["/cgi-bin", "/web-images", "/downloads", "/glimpse_index", "/pages/internal"]),
    "gitlab.ics.uci.edu": set(["/users", "/help"]),
    # not actually disallowed, but this guy publishes a lot of blogs, and then has a bunch of tags for each blog
    # each tag doesn't actually produce new content; several tags point to the same content
    # "ngs.ics.uci.edu": set(["/tag"]),
    # https://swiki.ics.uci.edu and https://wiki.ics.uci.edu has a lot of EXTREMELY low information value pages
    "swiki.ics.uci.edu": set([
        # a content file explorer that says I don't have read access anyway
        # "/doku.php/services:emailproofpoint",
        # no access to; must log in
        # "/doku.php/services:database:mysql:unprivileged-users",
        # leads to sitemap
        # "/doku.php/accounts:restore_unix_dot_files",
        # "/doku.php/commands:screen",
    ]),
    "wiki.ics.uci.edu": set([  # same as above
        # "/doku.php/services:emailproofpoint",
        # "/doku.php/services:database:mysql:unprivileged-users",
        # "/doku.php/accounts:restore_unix_dot_files",
        # "/doku.php/commands:screen",
    ]),
    # this part of the website leads to some really weird trap
    "cert.ics.uci.edu": set([
        "/EMWS09"
    ])

}

# paths that include these segments should be skipped
INVALID_PATH_SEGMENTS = set([
    "files/pdf",
    "file/pdf",
    # gitlab actually disallows most of anything containing /-/ in their robots.txt
    "/-/",
    # http://www.cert.ics.uci.edu/seminar/EMWS09/Nanda/.../seminar/Nanda is some terrible crawler trap that probably uses relative path URLs
    "/seminar/Nanda",
    # wiki: doku.php/accounts:* are 99% of the time Insufficient Privilege page
    "/accounts:",
    # is a PDF, does not end with .PDF
    "20-secret-sharing-aggregation-TKDE-shantanu"
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
    "redirect_to",
    # https://swiki.ics.uci.edu/doku.php/start?rev=X makes the rev query a crawler trap
    "rev=",
    # wiki/doku.php pages with queries that produce low information value pages
    "do=media",
    "do=login",
    "do=backlink",
    # "do=edit",
    "idx=",  # always leads to sitemap
    # gitlab, sorted=created_asc or sorted-created_desc are just reformats for data, thus are low information
    # "sort=created_"
])

# these fragments are associated with links that produce the exact same page, but pointing to a different section
# they are the first line of defense against the fragment issue; that is
# links with different fragments producing identical pages (because the domain and path are same)
# UPDATE: found out that you should just defragment all URLs, this is deprecated
INVALID_FRAGMENTS = set([
    "comment-",
    "respond"
])

# regex patterns used in validation
FILE_EXT_PATTERN = re.compile(
    r".*\.(css|js|bmp|gif|jpe?g|ico"
    + r"|png|tiff?|mid|mp2|mp3|mp4"
    + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
    + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|ppsx|odc|git|db|war|img|apk|bib|ff"
    + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
    + r"|epub|dll|cnf|tgz|sha1"
    + r"|thmx|mso|arff|rtf|jar|csv"
    + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$")

CALENDAR_TRAP_PATTERN = re.compile(
    r"(?:\d{2}|\d{4})\D+\d{1,2}\D+\d{1,2}|"
    + r"\d{1,2}\D+\d{1,2}\D+(?:\d{2}|\d{4})|"
    + r"(?:\d{2}|\d{4})\D+\d{1,2}|"
    + r"\d{1,2}\D+(?:\d{2}|\d{4})")

ANY_NUMBER_PATTERN = re.compile(r"\d+")
