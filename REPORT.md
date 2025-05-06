# Report

Answers to the deliverable questions are found at the end of this report, utilizing the definitions found below.

This report was created using output files found in `./Output/deliverables-05-04-15-03-52.txt`.

## Definitions

### Unique pages

A unique page is defined as the following:

- Pages that, when downloaded, return a 200 status code.
- Pages that, when downloaded, have a non-empty response body.
- Pages that have a defragmented response URL that has not been previously seen.
- Pages that have a response URL that is valid.

### Valid URLs

Valid URLs are defined as the following:

- URLs that fall within the domain names patterns specified.
- URLs that end with an invalid URL extension, such as `.pdf`, `.bin`, `.png`, etc.
- URLs that do not return a `608` error (this error mean they are blocked by robots.txt)
- URLs that don't lead to crawler traps, such as calendar traps, or `/page/X` that go on endlessly.
- URLs that point to webpages with low information value.

### Low Information Value

Low information value pages are defined as following:

- Pages that have valid URLs.
- Pages used to elicit script(s) to run whilst not providing any new information to the page, such as:
  - Links with queries including `action=XXX`, which typically prompts uploading, downloading, etc.
  - Links with queries including `ical=1`: which begins the download of calendar invite files.
  - Links with queries including `redirect_to=XXX` to another page, typically out of the domain names specified.
- Pages that immediately redirect to another page, especially since these pages contain no data themselves besides the redirection script.
- Pages that are locked behind authentication pages.

Pages with some information value are defined to have usable content that differentiates it from other page, even if the crawler chooses to do nothing with it. Thus, even if a page contains mostly data the crawler doesn't process (such as images), they are still considered to have information value. This definition justifies the choice of crawling the following subset of pages, since it considers them to have good enough informatoin value:

- - `http://www.ics.uci.edu/~eppstein/pix/*`
- - `http://www.ics.uci.edu/~ziv/ooad/*/sld*.htm`

## Deliverables

### (1) Unique pages found

26413

### (2) Longest page in terms of number of words

<http://www.ics.uci.edu/~eppstein/pubs/all.html>, with 12864 words

### (3) 50 most common words (ordered by frequency)

- research (82159)
- student (51297)
- science (46737)
- computer (46648)
- learning (42151)
- us (39938)
- graduate (39682)
- undergraduate (38878)
- data (34842)
- news (31528)
- faculty (30135)
- information (29439)
- community (25924)
- alumni (22281)
- view (21354)
- machine (20946)
- school (19903)
- people (18919)
- text (18420)
- statistics (17772)
- future (17099)
- may (16784)
- march (16748)
- search (16387)
- follow (16367)
- engineering (16290)
- contrast (15989)
- new (15896)
- support (15790)
- get (15379)
- next (15308)
- technical (14816)
- university (14683)
- corporate (14525)
- home (14488)
- one (14485)
- june (14107)
- academic (14069)
- tech (13673)
- contact (13331)
- health (13236)
- update (13172)
- content (13130)
- lab (12985)
- design (12764)
- time (12711)
- share (12705)
- accessibility (12380)
- impact (12360)
- image (12305)

### (4) Subdomains list (ordered alphabetically)

- accessibility.ics.uci.edu, 6
- acoi.ics.uci.edu, 94
- aiclub.ics.uci.edu, 1
- archive.ics.uci.edu, 170
- asterix.ics.uci.edu, 7
- betapro.proteomics.ics.uci.edu, 3
- biaslab.ics.uci.edu, 1
- capstone.cs.uci.edu, 8
- cbcl.ics.uci.edu, 1
- cdb.ics.uci.edu, 48
- cert.ics.uci.edu, 32
- checkin.ics.uci.edu, 5
- chemdb.ics.uci.edu, 47
- chenli.ics.uci.edu, 10
- circadiomics.ics.uci.edu, 6
- cloudberry.ics.uci.edu, 27
- cml.ics.uci.edu, 99
- code.ics.uci.edu, 14
- computableplant.ics.uci.edu, 103
- courselisting.ics.uci.edu, 4
- cradl.ics.uci.edu, 20
- create.ics.uci.edu, 7
- cs.ics.uci.edu, 13
- cs.uci.edu, 2
- cs260p-hub.ics.uci.edu, 2
- cwicsocal18.ics.uci.edu, 12
- cyberclub.ics.uci.edu, 3
- cybert.ics.uci.edu, 27
- datalab.ics.uci.edu, 1
- dgillen.ics.uci.edu, 32
- ds4all.ics.uci.edu, 2
- duttgroup.ics.uci.edu, 132
- dynamo.ics.uci.edu, 33
- edgelab.ics.uci.edu, 7
- elms.ics.uci.edu, 3
- emj.ics.uci.edu, 43
- esl.ics.uci.edu, 5
- evoke.ics.uci.edu, 3
- flamingo.ics.uci.edu, 29
- fr.ics.uci.edu, 3
- futurehealth.ics.uci.edu, 148
- gitlab.ics.uci.edu, 117
- grape.ics.uci.edu, 11
- graphics.ics.uci.edu, 8
- graphmod.ics.uci.edu, 1
- hack.ics.uci.edu, 2
- hai.ics.uci.edu, 7
- helpdesk.ics.uci.edu, 17
- hobbes.ics.uci.edu, 11
- hpi.ics.uci.edu, 5
- hub.ics.uci.edu, 4
- i-sensorium.ics.uci.edu, 6
- iasl.ics.uci.edu, 26
- icde2023.ics.uci.edu, 46
- ics.uci.edu, 4273
- ics45c-hub.ics.uci.edu, 2
- ics45c-staging-hub.ics.uci.edu, 2
- ics46-hub.ics.uci.edu, 2
- ics46-staging-hub.ics.uci.edu, 2
- ics53-hub.ics.uci.edu, 2
- ics53-staging-hub.ics.uci.edu, 2
- ieee.ics.uci.edu, 5
- industryshowcase.ics.uci.edu, 22
- informatics.ics.uci.edu, 2
- informatics.uci.edu, 21
- insite.ics.uci.edu, 7
- instdav.ics.uci.edu, 1
- ipubmed.ics.uci.edu, 1
- isg.ics.uci.edu, 249
- jgarcia.ics.uci.edu, 36
- julia-hub.ics.uci.edu, 2
- luci.ics.uci.edu, 4
- mailman.ics.uci.edu, 33
- malek.ics.uci.edu, 1
- mcs.ics.uci.edu, 10
- mdogucu.ics.uci.edu, 3
- mds.ics.uci.edu, 8
- mhcid.ics.uci.edu, 21
- mlphysics.ics.uci.edu, 18
- motifmap.ics.uci.edu, 2
- mover.ics.uci.edu, 24
- mswe.ics.uci.edu, 11
- mupro.proteomics.ics.uci.edu, 3
- nalini.ics.uci.edu, 7
- ngs.ics.uci.edu, 2024
- oai.ics.uci.edu, 5
- observium.ics.uci.edu, 1
- pepito.proteomics.ics.uci.edu, 5
- pgadmin.ics.uci.edu, 1
- plrg.ics.uci.edu, 16
- psearch.ics.uci.edu, 1
- radicle.ics.uci.edu, 6
- reactions.ics.uci.edu, 7
- redmiles.ics.uci.edu, 1
- riscit.ics.uci.edu, 3
- scale.ics.uci.edu, 7
- scratch.proteomics.ics.uci.edu, 4
- sdcl.ics.uci.edu, 85
- seal.ics.uci.edu, 48
- selectpro.proteomics.ics.uci.edu, 7
- sherlock.ics.uci.edu, 7
- sli.ics.uci.edu, 303
- speedtest.ics.uci.edu, 1
- staging-hub.ics.uci.edu, 2
- stairs.ics.uci.edu, 4
- stat.uci.edu, 3
- statconsulting.ics.uci.edu, 5
- statistics-stage.ics.uci.edu, 11
- student-council.ics.uci.edu, 4
- studentcouncil.ics.uci.edu, 14
- summeracademy.ics.uci.edu, 6
- support.ics.uci.edu, 3
- svn.ics.uci.edu, 1
- swiki.ics.uci.edu, 602
- tad.ics.uci.edu, 3
- tastier.ics.uci.edu, 1
- transformativeplay.ics.uci.edu, 54
- tutoring.ics.uci.edu, 5
- tutors.ics.uci.edu, 1
- ugradforms.ics.uci.edu, 1
- unite.ics.uci.edu, 9
- vision.ics.uci.edu, 210
- wearablegames.ics.uci.edu, 11
- wics.ics.uci.edu, 1014
- wiki.ics.uci.edu, 606
- www-db.ics.uci.edu, 25
- www.cert.ics.uci.edu, 20
- www.cs.uci.edu, 9
- www.graphics.ics.uci.edu, 7
- www.ics.uci.edu, 13631
- www.informatics.ics.uci.edu, 1
- www.informatics.uci.edu, 1136
- www.stat.uci.edu, 226
- xtune.ics.uci.edu, 6
