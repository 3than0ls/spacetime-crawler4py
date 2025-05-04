# Deliverables

## Unique pages

A unique page is defined as the following:

- Pages that, when downloaded, return a 200 status code.
- Pages that, when downloaded, have a non-empty response body.
- Pages that have a defragmented response URL that has not been previously seen.
- Pages that have a response URL that is valid.

## Valid URLs

Valid URLs are defined as the following:

- URLs that fall within the domain names patterns specified.
- URLs that end with an invalid URL extension, such as `.pdf`, `.bin`, `.png`, etc.
- URLs that do not return a `608` error (this error mean they are blocked by robots.txt)
- URLs that don't lead to crawler traps, such as calendar traps, or `/page/X` that go on endlessly.
- URLs that point to webpages with low information value.

## Low Information Value

Low information value pages are defined as following:

- Pages that have valid URLs.
- Pages used to elicit script(s) to run whilst not providing any new information to the page, such as:
  - Links with queries including `action=XXX`, which typically prompts uploading, downloading, etc.
  - Links with queries including `ical=1`: which begins the download of calendar invite files.
  - Links with queries including `redirect_to=XXX` to another page, typically out of the domain names specified.
- Pages that immediately redirect to another page, especially since these pages contain no data themselves besides the redirection script.
- Pages that are locked behind authentication pages.

Pages with some information value are defined to have usable content that differentiates it from other page, even if the crawler chooses to do nothing with it. Thus, even if a page contains mostly data the crawler doesn't process (such as images), they are still considered to have information value. This definition justifies the choice of crawling the following subset of pages, since it considers them to have good enough informatoin value:

- `http://www.ics.uci.edu/~eppstein/pix/*`
- `http://www.ics.uci.edu/~ziv/ooad/*/sld*.htm`



ICS has a lot of article pages with URLs that are formatted as following: `https://ics.uci.edu/YYYY/MM/DD/*`, found under `https://ics.uci.edu/happening/news/page/X` where X goes up to 135

Test: only allow calendars if they are found at the end of the path, and only allow /page/X to go up to 200 (if X is not a number, let it go through)