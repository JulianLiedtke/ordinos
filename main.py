"""Main file of the Ordinos"""

import logging
import random

from src.crypto.paillier_abb import PaillierABB
from src.election.borda.borda_election_system import Borda
from src.election.borda.borda_implementations import (
    EscElection, FisWorldCup, MedalTableSystem)
from src.election.condorcet.condorcet_election_system import Condorcet
from src.election.condorcet.condorcet_implementations import (
    Copeland, MiniMaxMarginsSmith, MiniMaxWinningVotesSmith)
from src.election.condorcet.condorcet_no_winner_evaluations import MiniMaxMarginsEvaluation, SchulzeEvaluation, SmithEvaluation, SmithFastEvaluation, WeakCondorcetEvaluation
from src.election.election_authority import ElectionAuthority
from src.election.instant_runoff_voting.irv_election_system import (
    IRVElectionSystemAlternative, IRVElectionSystemNormal)
from src.election.single_vote.single_vote_election_system import \
    SingleVoteElection
from src.election.parliamentary_ballot.parliamentary_ballot_properties import ParliamentaryBallotProperties
from src.protocols.sublinear import SubLinearProtocolSuite
from src.util.csv_writer import CSV_Writer
from src.util.logging import setup_logging
from src.util.point_vote import PointVote
from src.util.position_vote import PositionVote

if __name__ == '__main__':
    CSV_Writer.init_writer()
    # set general parameters of Ordinos
    key_generator = lambda: PaillierABB.gen_trustees(64, 2, 2, SubLinearProtocolSuite) #to run with Paillier
    
    setup_logging(logging.INFO)
    n_cand = 5
    n_votes = 500
    random.seed(3)
    # votes = PointVote.generate_random_point_votes(n_votes=n_votes, n_cand=n_cand, max_points=5)
    votes = PositionVote.generate_random(n_votes, n_cand)

    # ElectionAuthority(key_generator, ParliamentaryBallotProperties(n_cand, 10, False, 0)).add_votes_and_evaluate(votes)

    # ElectionAuthority(key_generator, SingleVoteElection(n_cand)).add_votes_and_evaluate(votes)

    # # borda variants
    ElectionAuthority(key_generator, Borda(n_cand, point_limit=int((n_cand+1)*n_votes/2))).add_votes_and_evaluate(votes) # original Borda point limit
    ElectionAuthority(key_generator, Borda(n_cand, num_winners=4)).add_votes_and_evaluate(votes) # original Borda set winner count
    ElectionAuthority(key_generator, Borda(n_cand)).add_votes_and_evaluate(votes) # original Borda
    # ElectionAuthority(key_generator, Borda(n_cand, list_of_points=[1])).add_votes_and_evaluate(votes) # equals SingleVoteSystem
    # ElectionAuthority(key_generator, Borda(n_cand, list_of_points=[3,2,1])).add_votes_and_evaluate(votes)
    # ElectionAuthority(key_generator, Borda(n_cand, list_of_points=[10,9,8,7,6,5,4,3,2,1], allow_less_cands=True, begin_with_last=False)).add_votes_and_evaluate(votes)
    # ElectionAuthority(key_generator, Borda(n_cand, list_of_points=[10,9,8,7,6,5,4,3,2,1], allow_less_cands=True, begin_with_last=True)).add_votes_and_evaluate(votes)
    # ElectionAuthority(key_generator, EscElection(n_cand)).add_votes_and_evaluate(votes)
    # ElectionAuthority(key_generator, MedalTableSystem(n_cand, n_votes)).add_votes_and_evaluate(votes)
    # ElectionAuthority(key_generator, FisWorldCup(n_cand, n_votes)).add_votes_and_evaluate(votes)

    # # condorcet variants
    ElectionAuthority(key_generator, Condorcet(n_cand, leak_better_half=False)).add_votes_and_evaluate(votes)
    ElectionAuthority(key_generator, Condorcet(n_cand, [WeakCondorcetEvaluation], evaluate_condorcet=False)).add_votes_and_evaluate(votes)
    ElectionAuthority(key_generator, Copeland(n_cand, leak_max_points=True, evaluate_condorcet=False)).add_votes_and_evaluate(votes)
    ElectionAuthority(key_generator, Copeland(n_cand, leak_max_points=False, evaluate_condorcet=False)).add_votes_and_evaluate(votes)
    ElectionAuthority(key_generator, Condorcet(n_cand, [MiniMaxMarginsEvaluation], evaluate_condorcet=False)).add_votes_and_evaluate(votes)
    ElectionAuthority(key_generator, Condorcet(n_cand, [SmithEvaluation], evaluate_condorcet=False)).add_votes_and_evaluate(votes)
    ElectionAuthority(key_generator, Condorcet(n_cand, [SmithFastEvaluation], evaluate_condorcet=False)).add_votes_and_evaluate(votes)
    ElectionAuthority(key_generator, Condorcet(n_cand, [SchulzeEvaluation], evaluate_condorcet=False)).add_votes_and_evaluate(votes)

    # irv variants
    # ElectionAuthority(key_generator, IRVElectionSystemNormal(n_cand, bits_int=16, sys_id=0)).add_votes_and_evaluate(votes)
    # ElectionAuthority(key_generator, IRVElectionSystemAlternative(n_cand, bits_int=16, sys_id=5)).add_votes_and_evaluate(votes) # generic vote couldn't be adapted
