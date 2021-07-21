import sys
import logging
from src.crypto.plain_abb import PlainABB
from src.election.condorcet.condorcet_election_system import Condorcet
from src.election.condorcet.condorcet_no_winner_evaluations import \
    SmithEvaluation
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
    smith_set_size_counters = [0 for i in range(n_cand)]

    for i in range(rounds):
        smith_system = ElectionAuthority(key_generator, Condorcet(n_cand, [SmithEvaluation], leak_better_half=False))
        votes = PointVote.generate_random_point_votes(n_votes, n_cand, max_points=n_cand*10)
        smith_set = smith_system.add_votes_and_evaluate(votes)

        smith_set_size = len(smith_set)
        smith_set_size_counters[smith_set_size-1] +=1

    print(smith_set_size_counters)
