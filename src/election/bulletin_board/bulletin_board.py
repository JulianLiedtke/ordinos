import logging
from time import time

log = logging.getLogger(__name__)


class BulletinBoard:

    def __init__(self, bb_functions, abb, n_cand):
        self.votes = []
        self.aggregation_time = 0

        # init vote aggregation
        startTime = time()
        self.vote_aggregation = bb_functions.get_initial_vote_aggregation(abb, n_cand)
        self.aggregate_vote = bb_functions.aggregate_vote
        self.aggregation_time += time() - startTime

    def add_vote(self, vote):
        """
        add vote to list of votes and possible aggregation
        | vote has to be valid
        """
        startTime = time()

        self.aggregate_vote(self.vote_aggregation, vote)
        self.votes.append(vote)

        self.aggregation_time += time() - startTime

    def get_votes(self):
        """returns list of votes, vote_aggregation and time to aggregate"""
        return self.votes, self.vote_aggregation, self.aggregation_time
