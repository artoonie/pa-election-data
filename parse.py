import pprint
import csv
import os
import re

class OneSeatData:
    year:int
    month:int
    day:int
    electiontype:str

    def __init__(self, countyData):
        self.year = countyData.year
        self.month = countyData.month
        self.day = countyData.day
        self.electiontype = countyData.electiontype

    def __repr__(self):
        return "%d-%d-%d: %s" % (self.year, self.month, self.day, self.electiontype)

    def __hash__(self):
        return hash((self.year, self.month, self.day, self.electiontype))

    def __eq__(self, other):
        return (self.year, self.month, self.day, self.electiontype) == (other.year, other.month, other.day, other.electiontype)

    def __ne__(self, other):
        return not(self == other)

class SeatPerCountyMetadata:
    year:int
    month:int
    day:int
    electiontype:str
    county:str

    def __init__(self, matchesDict):
        self.year = int(matchesDict['year'])
        self.month = int(matchesDict['month'])
        self.day = int(matchesDict['day'])
        self.electiontype = matchesDict['electiontype']
        self.county = matchesDict['county']

    def __str__(self):
        return "%d-%d-%d: %s (%s)" % (self.year, self.month, self.day, self.electiontype, self.county)

    def __repr__(self):
        return str(self)

    def data_without_county(self):
        return (self.year, self.month, self.day, self.electiontype)

class PrecinctResult:
    office:str
    candidatesToVotes:dict

def parseFile(filepath):
    d = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d.append(row)
    return d

def parseAllFiles(maindir, fastmode=False):
    maindir = 'openelections-data-pa'
    regex = re.compile('(?P<year>20[0-2][0-9])(?P<month>[0-9][0-9])(?P<day>[0-9][0-9])__pa__(?P<electiontype>[^_]*)__(?P<county>[^_]*)__precinct.csv')
    countyData = {}
    for year in os.listdir(maindir):
        try:
            intyear = int(year)
        except ValueError:
            continue

        yeardir = os.path.join(maindir, year, 'counties')
        if not os.path.exists(yeardir):
            print("No counties listed in", yeardir)
            continue

        for filename in os.listdir(yeardir):
            filepath = os.path.join(yeardir, filename)
            matches = regex.match(filename)
            if not matches:
                print("Invalid filename:", filepath)
                continue

            print("Parsing ", filepath)
            seatPerCountyMetadata = SeatPerCountyMetadata(matches.groupdict())
            result = parseFile(filepath)
            countyData[seatPerCountyMetadata] = result

            if fastmode:
                break
    return countyData

def parseVotesFromOneRowOfData(rawDataResult):
    ignore = ('Write-ins', 'Write In', 'Write In Votes', 'WRITE-IN', 'Under Votes', 'Over Votes', 'Cast Votes', '')
    candidateName = rawDataResult['candidate'] 
    if candidateName in ignore:
        return

    votes = rawDataResult['votes']
    if votes == '':
        return
    votes = votes.replace(',', '')

    return int(votes)

def getPrecinctResultsPerElection(data):
    ignore = ('Ballots Cast - Blank',
              'Ballots Cast',
              'Registered Voters',
              'Late Absentee Turnout',
              'Late Military Absentee Turnout',
              'Emergency Turnout',
              'Election Day Edge Turnout',
              'Absentee Turnout',
              'Provisional Turnout',
              'Straight House',
              'STRAIGHT HOUSE',
              'STRAIGHT PARTY',
              '')
    ignoreIfEndsWithLowercase = 'referendum'
    precinctResultsPerElection = {}
    for seatPerCountyMetadata, results in data.items():
        oneSeatData = OneSeatData(seatPerCountyMetadata)
        if oneSeatData not in precinctResultsPerElection:
            precinctResultsPerElection[oneSeatData] = {}

        precinctResults = precinctResultsPerElection[oneSeatData]

        for rawDataResult in results:
            office = rawDataResult['office']
            if office in ignore:
                continue
            if office.lower().endswith(ignoreIfEndsWithLowercase):
                continue

            votes = parseVotesFromOneRowOfData(rawDataResult)
            if not votes:
                # either 0 votes, or ignored candidate name
                continue

            if office not in precinctResults:
                precinctResults[office] = {}

            candidateName = rawDataResult['candidate']
            if candidateName not in precinctResults[office]:
                precinctResults[office][candidateName] = 0
            precinctResults[office][candidateName] += votes
    return precinctResultsPerElection

def main():
    maindir = 'openelections-data-pa'
    data = parseAllFiles(maindir, fastmode=False)
    results = getPrecinctResultsPerElection(data)
    pprint.pprint(results)

    with open('results.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['year', 'month', 'day', 'electiontype', 'office', 'num candidates', 'percent winner won with'])
        for oneSeatData, precinctResults in results.items():
            for office, votes in precinctResults.items():
                totalVotes = sum(votes.values())
                maxVotes = max(votes.values())
                
                print('%s "%s" had %d candidates, and the winner won with %d%%' % (str(oneSeatData), office, len(votes), round(100*maxVotes/totalVotes)))
                csvwriter.writerow([oneSeatData.year, oneSeatData.month, oneSeatData.day, oneSeatData.electiontype, office, len(votes), maxVotes/totalVotes])
            print()


if __name__ == "__main__":
    main()
