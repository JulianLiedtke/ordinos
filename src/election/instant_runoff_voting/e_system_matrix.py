from src.util.old_files.former_e_system import Former_ESystem
import numpy as np
import logging

log = logging.getLogger(__name__)

class ESystemMatrix(Former_ESystem):

    def init_votes(self):
        """ inits an empty list of ballots """
        self.votes = []

    def addVote(self, vote):
        """ adds a vote as encrypted numpy matrix, no action for incorrect shape or entries"""
        if vote.shape != (self.num_candidates, self.num_candidates):
            log.warning("incorrect shape")
            return

        for x in range(self.num_candidates):
            row_sum = self.crypto.encrypt(0)
            col_sum = self.crypto.encrypt(0)
            for y in range(self.num_candidates):
                row_sum = self.evaluator.add(row_sum, vote[x,y])
                col_sum = self.evaluator.add(col_sum, vote[y,x])
            if self.crypto.decrypt(row_sum) != 1 or self.crypto.decrypt(col_sum) != 1:
                log.warning("incorrect entries")
                return
        self.votes.append(vote)

    def getVotes(self):
        return np.copy(self.votes)

    def printVotes(self):
        for vote in self.votes:
            log.info(vote)

    def rank(self):
        pass

    def delete_column(self, col):
        #delete the given matrix-column in each vote
        new_votes = []
        for vote in self.votes:
            new_votes.append(np.delete(vote,col,1))
        self.votes = new_votes
        self.evaluator.set_votes(new_votes)

    def setVotes(self, votes):
        self.votes = votes
        self.evaluator.set_votes(votes)
