

from src.util.point_vote import PointVote
from src.election.condorcet.condorcet_election_system import Condorcet
from src.election.condorcet.condorcet_implementations import Copeland, MiniMaxMarginsSmith
from src.election.condorcet.condorcet_no_winner_evaluations import SmithEvaluation, SchulzeEvaluation
from src.util.logging import setup_logging
import logging
from src.election.election_authority import ElectionAuthority
from src.crypto.paillier_abb import PaillierABB
from src.protocols.sublinear import SubLinearProtocolSuite


def test_condorcet_without_winner(system):
    system.add_generic_vote(PointVote([4, 3, 2, 1]), count=3)
    system.add_generic_vote(PointVote([1, 2, 3, 4]), count=1)
    system.add_generic_vote(PointVote([1, 4, 3, 2]), count=1)
    system.add_generic_vote(PointVote([3, 1, 4, 2]), count=2)
    system.trigger_evaluation()


if __name__ == '__main__':
    setup_logging(logging.DEBUG)

    key_generator = lambda: PaillierABB.gen_trustees(64, 3, 2, SubLinearProtocolSuite) #to run with Paillier
    test_condorcet_without_winner(ElectionAuthority(key_generator, Condorcet(4, additional_evaluators=[SmithEvaluation, SchulzeEvaluation])))
    test_condorcet_without_winner(ElectionAuthority(key_generator, Copeland(4)))
    test_condorcet_without_winner(ElectionAuthority(key_generator, MiniMaxMarginsSmith(4)))
