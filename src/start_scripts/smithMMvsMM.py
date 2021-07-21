from src.util.logging import setup_logging
import logging
import sys

from src.crypto.plain_abb import PlainABB
from src.election.condorcet.condorcet_election_system import Condorcet
from src.election.condorcet.condorcet_no_winner_evaluations import (
    MiniMaxMarginsEvaluation, MiniMaxWinningVotesEvaluation, SmithEvaluation)
from src.election.election_authority import ElectionAuthority
from src.protocols.protocol_suite import EmptyProtocolSuite
from src.util.logging import setup_logging
from src.util.point_vote import PointVote


if __name__ == '__main__':
    setup_logging(logging.WARNING)

    key_generator = lambda: PlainABB.gen_trustees(64, 2, 2, EmptyProtocolSuite)
    n_cand = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    n_votes = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    votes_with_difference = []

    for i in range(rounds):
        smit_mm_system = ElectionAuthority(key_generator, Condorcet(n_cand, [SmithEvaluation, MiniMaxWinningVotesEvaluation], leak_better_half=False))
        mm_system = ElectionAuthority(key_generator, Condorcet(n_cand, [MiniMaxWinningVotesEvaluation], leak_better_half=False))
        votes = PointVote.generate_random_point_votes(n_votes, n_cand, min_points=-1, max_points=3)
        smith_mm = smit_mm_system.add_votes_and_evaluate(votes)
        mm = mm_system.add_votes_and_evaluate(votes)

        if smith_mm != mm:
            votes_with_difference.append(votes)

    print(str(len(votes_with_difference)) + ' of ' + str(rounds) + ' are different')
    print(str(votes_with_difference))
