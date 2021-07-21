from src.util.old_files.former_e_system import Former_ESystem
import bisect
from itertools import permutations
import logging

log = logging.getLogger(__name__)

class ESystemTuple(Former_ESystem):

    def init_votes(self):
        """ create dict of votes, initialized with zero votes per candidate"""
        self.num_voter = 0
        self.eliminated = []
        self.votes = dict()
        tuples = list(permutations(list(range(1, self.num_candidates+1))))
        zero = self.crypto.encrypt(0)
        for tuple in tuples:
            self.votes[tuple] = zero

    def addVote(self, vote):
        """ adds a vote (vote is a dictionary!) """
        self.num_voter += 1
        for tuple, num_votes in vote.items():
            self.votes[tuple] = self.crypto.add(self.votes[tuple], num_votes)

    def getVotes(self):
        return self.votes.copy()

    def printVotes(self):
        for tuple, value in self.votes.items():
            log.info("Tupel " + str(tuple) + " verschlüsselte Anzahl: " + str(value))

    def rank(self):
        pass

    def delete_entry(self, cand):
        """ save the eliminated candidate and update tuples of the votes"""

        #insert the id into the sorted list of eliminated candidates
        bisect.insort(self.eliminated, cand)
        old_votes = self.votes
        new_votes = dict()

        for tuple in old_votes.keys():
            #add votes of previous tuple to votes of the equivalent new tuple (after deletion of eliminated candidate)
            index = tuple.index(cand)
            new_tuple = tuple[ : index ] + tuple[index+1 : ]
            if new_tuple not in new_votes:
                new_votes[new_tuple] = self.crypto.encrypt(0)
            new_votes[new_tuple] = self.crypto.add(new_votes[new_tuple], old_votes[tuple])
        self.votes = new_votes
        self.evaluator.set_votes(new_votes)

    def get_eliminated(self):
        """ return id's of eliminated candidates (sorted list) """
        return self.eliminated.copy()

    def setVotes(self, votes):
        self.votes = votes
        self.evaluator.set_votes(votes)

    def get_num_voter(self):
        return self.num_voter