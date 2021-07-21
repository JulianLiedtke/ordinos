
from src.election.election_properties import ElectionProperties
from src.util.point_vote import IllegalVoteException
from src.election.bulletin_board.simple_addition_bulletin_board import \
    SimpleAdditionBulletinBoard
from src.election.parliamentary_ballot.parliamentary_evaluation import ParliamentaryEvaluation

class ParliamentaryBallotProperties(ElectionProperties):

    def __init__(self, candidates, n_seats, secret_residual, clause):
        """
        :param num_seats: number of seats in parliament
        :param secret_residual: pass true iff secred version is required
        :param clause: number of required votes for a party to obtain seats
        """
        super().__init__(candidates, SimpleAdditionBulletinBoard, logger_name_extension=str(n_seats)+str(secret_residual)+str(clause))
        self.n_seats = n_seats
        self.secret_residual = secret_residual
        self.clause = clause

    def get_evaluator(self, n_votes, abb):
        eval = ParliamentaryEvaluation(n_votes, self.n_seats, self.secret_residual, self.clause)
        return eval

    def generate_valid_vote(self, generic_vote, abb):
        """ inits a dictionary containing each candidate with zero votes """
        vote = {}

        # set every cand to 0 and find cand with biggest points, prefer lower numbers if equals
        for cand in range(self.n_cand):
            vote[cand] = abb.enc(0)

        # set index with highest points to 1
        winners = generic_vote.get_ranking_map()[1]
        if len(winners) != 1:
            raise IllegalVoteException("More or less than one winner")
        vote[winners[0]] = abb.enc(1)
        return vote