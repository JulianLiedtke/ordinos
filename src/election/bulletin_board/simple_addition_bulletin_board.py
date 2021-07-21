import logging

from src.election.bulletin_board.bulletin_board_functions import EmptyBulletinBoardFunctions
from src.util.utils import init_empty_cand_dict

log = logging.getLogger(__name__)


class SimpleAdditionBulletinBoard(EmptyBulletinBoardFunctions):

    def get_initial_vote_aggregation(self, abb, n_cand):
        enc_zero = abb.enc_no_r(0)
        """ inits a dictionary containing each candidate with zero votes """
        aggregatedVotes = init_empty_cand_dict(n_cand, enc_zero)

        return aggregatedVotes

    def aggregate_vote(self, vote_aggregation, new_vote):
        """ adds a vote by adding the ciphertexts to the current encrypted votes """
        for cand in range(len(vote_aggregation)):
            vote_aggregation[cand] += new_vote[cand]
