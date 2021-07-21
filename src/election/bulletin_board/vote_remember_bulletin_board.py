import logging

import numpy

from src.election.bulletin_board.bulletin_board_functions import \
    EmptyBulletinBoardFunctions

log = logging.getLogger(__name__)


class VoteRememberBulletinBoardFunctions(EmptyBulletinBoardFunctions):

    def get_initial_vote_aggregation(self, abb, n_cand):
        """ inits a dictionary containing each candidate with zero votes """
        return []

    def aggregate_vote(self, vote_aggregation, new_vote):
        vote_aggregation.append(new_vote)
