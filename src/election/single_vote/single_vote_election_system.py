import logging

from src.election.bulletin_board.simple_addition_bulletin_board import \
    SimpleAdditionBulletinBoard
from src.election.election_properties import ElectionProperties
from src.election.evaluation.simple_winner_evaluation import \
    SimpleWinnerEvaluation
from src.util.point_vote import IllegalVoteException

log = logging.getLogger(__name__)


class SingleVoteElection(ElectionProperties):

    def __init__(self, candidates):
        super().__init__(candidates, SimpleAdditionBulletinBoard)
        self.MAX_POINTS_PER_VOTE = 1

    def generate_valid_vote(self, generic_vote, abb):
        """ inits a dictionary containing each candidate with zero votes """
        vote_decrypted = {}

        # set every cand to 0 and find cand with biggest points, prefer lower numbers if equals
        for cand in range(self.n_cand):
            vote_decrypted[cand] = 0

        # set index with highest points to 1
        winners = generic_vote.get_position(1)
        if len(winners) != 1:
            raise IllegalVoteException("More or less than one winner")
        vote_decrypted[winners[0]] = 1

        vote_encrypted = {}
        log.debug(str(vote_decrypted))
        for cand in range(self.n_cand):
            vote_encrypted[cand] = abb.enc(vote_decrypted[cand])
        return vote_encrypted

    def get_evaluator(self, n_votes, abb):
        eval = SimpleWinnerEvaluation(abb.get_bits_for_size(n_votes * self.MAX_POINTS_PER_VOTE))
        return eval
