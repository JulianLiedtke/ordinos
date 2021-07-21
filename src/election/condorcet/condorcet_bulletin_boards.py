import logging

import numpy

from src.election.bulletin_board.bulletin_board_functions import \
    EmptyBulletinBoardFunctions
from time import time

log = logging.getLogger(__name__)


class CondorcetBulletinBoard(EmptyBulletinBoardFunctions):

    def get_initial_vote_aggregation(self, abb, n_cand):
        """ inits a dictionary containing each candidate with zero votes """
        preferenceMatrix = [[abb.enc_zero for i in range(n_cand)] for i in range(n_cand)]
        doubled_borda_points_sum = [abb.enc_zero for i in range(n_cand)]

        return [preferenceMatrix, doubled_borda_points_sum]

    def aggregate_vote(self, vote_aggregation, new_vote):
        """ adds a vote by adding matrices element by element """
        vote_aggregation[0] = numpy.add(vote_aggregation[0], new_vote[0])
        if len(new_vote[1]) > 0:
            vote_aggregation[1] = numpy.add(vote_aggregation[1], new_vote[1])
