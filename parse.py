import pprint
import csv
import os
import re

class PrecinctResult:
    office:str
    candidatesToVotes:dict

class OneElection:
    electionName:str
    office:str
    district:str

    def __init__(self, oneRow):
        self.electionName = oneRow.electionName
        self.office = oneRow.office
        self.district = oneRow.district

    def __hash__(self):
        return hash((self.electionName, self.office, self.district))

    def __eq__(self, other):
        return (self.electionName, self.office, self.district) == (other.electionName, other.office, other.district)

class OneRow:
    electionName:str
    county:str
    office:str
    district:str
    candidateName:str
    numVotes:int

    def __init__(self, rawRowData):
        self.electionName = rawRowData['Election Name']
        self.county = rawRowData['County Name']
        self.office = rawRowData['Office Name']
        self.district = rawRowData['District Name']
        self.candidateName = rawRowData['Candidate Name']
        self.numVotes = int(rawRowData['Votes'].replace(',', ''))

    def __repr__(self):
        return "%s (%s) for %s in %s: %s received %d votes" % (self.electionName, self.county, self.office, self.district, self.candidateName, self.numVotes)


def parseFile(filepath):
    d = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d.append(OneRow(row))
    return d

def parseAllFiles(maindir):
    dataPerElection = []
    for filename in os.listdir(maindir):
        if not filename.endswith('.CSV'):
            continue
        filepath = os.path.join(maindir, filename)

        print("Parsing ", filepath)
        result = parseFile(filepath)
        dataPerElection.append(result)

    return dataPerElection

def getPrecinctResultsPerElection(data):
    resultsPerElection = {}
    for election in data:
        for row in election:
            election = OneElection(row)

            # Add election to dataset if we haven't seen it before
            if election not in resultsPerElection:
                resultsPerElection[election] = {}
            results = resultsPerElection[election]

            # Initialize num votes if needed
            if row.candidateName not in results:
                results[row.candidateName] = 0

            # Accumulate votes
            results[row.candidateName] += row.numVotes
    return resultsPerElection

def main():
    maindir = 'downloads'
    data = parseAllFiles(maindir)
    resultsPerElection = getPrecinctResultsPerElection(data)
    pprint.pprint(resultsPerElection)

    with open('results.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['electionname', 'district', 'office', 'num candidates', 'percent winner won with', 'all running candidates'])
        for election, votes in resultsPerElection.items():
            totalVotes = sum(votes.values())
            maxVotes = max(votes.values())
            if totalVotes == 0:
                continue
            
            csvwriter.writerow([election.electionName, election.district, election.office, len(votes), maxVotes/totalVotes, *votes.keys()])


if __name__ == "__main__":
    main()
