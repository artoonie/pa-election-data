# What is this?
All the CSVs for all statewide elections available from the Pennsylvania Department of State, dating back to the year 2000.
Two files:
1. A downloader, which downloads these CSVs one at a time using selenium
1. A parser, which extracts statewide data from these CSVs, aggregating their county-level data

# Do you need this?
Pennsylvania provides election data in a consistent format starting in 2000.
That data is available here: https://www.electionreturns.pa.gov/ReportCenter/Reports

They also allow you to browse the data on the web is a really pleasing format, e.g.:
https://www.electionreturns.pa.gov/General/SummaryResults?ElectionID=72&ElectionType=G&IsActive=0

This repo is only if you want to download ALL the data, rather than browse it.
I did the work of manually extracting each CSV, and placing it in the `outputs` folder.
You can go ahead and use that data directly.
