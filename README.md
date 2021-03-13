# Pennsylvania Election Data, 2006-2020
Parsed and aggregated data from the Pennsylvania Secretary of State's official election reports for every election between 2006 and 2020.

# Use cases
Use it how you like.

We used it to determine how often candidates win without a majority. Indeed, whenever there are 3 or more candidates running for a seat, the winner is more likely than not to have _not_ reached a majority: instad, they receive a plurality of the votes with less than 50% of the total.

This means that most voters voted _against_ the winner. We believe this shows that we need a new system, like Ranked Choice Voting, that ensures that majorities elect the winner.

# What's in the repo
## Data
We scraped the PA Secretary of State website for all CSVs for all elections they had available. This data is available in the `outputs` directory.

## Scripts
1. `download.py`: Downloads CSVs from pa.gov using selenium. Generates `outputs/downloads/*.CSV`.
2. `parse.py`: Extracts statewide data from these CSVs, aggregating their county-level data. Generates `outputs/results.csv`.

The downloader works using a headless Chrome instance to click buttons on pa.gov to download all the data, since the data isn't easily accessible without user interaction.

# Do you need this?
Pennsylvania provides election data in a consistent format starting in 2000.
That data is available here: https://www.electionreturns.pa.gov/ReportCenter/Reports

They also allow you to browse the data on the web is a really pleasing format, e.g.:
https://www.electionreturns.pa.gov/General/SummaryResults?ElectionID=72&ElectionType=G&IsActive=0

This repo is only if you want to download ALL the data, rather than browse it.
I did the work of manually extracting each CSV, and placing it in the `outputs` folder.
You can go ahead and use that data directly.
For most users, using electionreturns.pa.gov directly will make more sense than using this repo.
