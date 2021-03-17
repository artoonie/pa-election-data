import csv
import os
import re

class PrecinctResult:
    office:str
    candidatesToVotes:dict

class OneElection:
    ballotName:str
    electionName:str
    office:str
    district:str
    party:str # only relevant if isPrimary
    year:int
    isSingleWinner:bool
    isSpecial:bool
    isPrimary:bool

    def __init__(self, ballotName, oneRow):
        self.ballotName = ballotName
        self.electionName = oneRow.electionName
        self.office = oneRow.office
        self.district = oneRow.district

        self.year = int(self.ballotName[0:4])

        self.isSingleWinner = self.is_single_winner(self.office)
        self.isPrimary = 'Primary' in ballotName
        self.isSpecial = 'Special' in ballotName

        self.party = oneRow.party if self.isPrimary else None

    @classmethod
    def is_single_winner(self, office):
        known_single_winner_substrings = (
            "Representative in",
            "President of the United States",
            "Attorney General",
            "State Treasurer",
            "Representative in",
            "Senator in",
            "United States Senator",
            "Auditor General",
            "Governor",
            "Lieutenant Governor")
        return any(substring in office for substring in known_single_winner_substrings)

    def _fields(self):
        if self.isPrimary:
            return (self.ballotName, self.electionName, self.office, self.district, self.party)

        return (self.ballotName, self.electionName, self.office, self.district)

    def __hash__(self):
        return hash(self._fields())

    def __eq__(self, other):
        return self._fields() == other._fields()

class OneRow:
    electionName:str
    county:str
    office:str
    party:str
    district:str
    candidateName:str
    numVotes:int

    def __init__(self, rawRowData):
        self.electionName = rawRowData['Election Name']
        self.county = rawRowData['County Name']
        self.office = rawRowData['Office Name']
        self.district = rawRowData['District Name']
        self.candidateName = rawRowData['Candidate Name']
        self.party = rawRowData['Party Name']
        votes = rawRowData['Votes']
        if votes == '':
            votes = '0'
        self.numVotes = int(votes.replace(',', ''))

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
    dataPerBallotName = {}
    for filename in os.listdir(maindir):
        if not filename.endswith('.CSV'):
            continue
        filepath = os.path.join(maindir, filename)

        print("Parsing ", filepath)
        result = parseFile(filepath)
        dataPerBallotName[filename] = result

    return dataPerBallotName

def getPrecinctResultsPerElection(dataPerBallotName):
    resultsPerElection = {}
    for ballotName, election in dataPerBallotName.items():
        for row in election:
            election = OneElection(ballotName, row)

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
    dataPerBallotName = parseAllFiles(maindir)
    resultsPerElection = getPrecinctResultsPerElection(dataPerBallotName)

    with open('results.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['year',
                            'ballotname',
                            'electionname',
                            'district',
                            'office',
                            'party (if primary)',
                            'special election?',
                            'primary?',
                            'single-winner?',
                            'num candidates',
                            'percent winner won with',
                            *['candidate %d'%d for d in range(1,11)]])
        for election, votes in resultsPerElection.items():
            totalVotes = sum(votes.values())
            maxVotes = max(votes.values())
            if totalVotes == 0:
                continue

            eachVotePct = [v/totalVotes for v in votes.values()]
            namesAndVotes = list(zip(eachVotePct, votes.keys()))
            namesAndVotes.sort(reverse=True)
            namesAndVotes = ["%s (%02.1f%%)" % (nv[1], 100*nv[0]) for nv in namesAndVotes]
            
            csvwriter.writerow([election.year,
                                election.ballotName,
                                election.electionName,
                                election.district,
                                election.office,
                                election.party,
                                election.isSpecial,
                                election.isPrimary,
                                election.isSingleWinner,
                                len(votes),
                                maxVotes/totalVotes,
                                *namesAndVotes])


if __name__ == "__main__":
    main()
