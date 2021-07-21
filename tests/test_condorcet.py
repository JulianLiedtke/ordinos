import json
import logging
import math
import time
import unittest
from time import sleep, time

from src.crypto.paillier_abb import PaillierABB
from src.crypto.plain_abb import PlainABB
from src.election.condorcet.condorcet_election_system import Condorcet
from src.election.condorcet.condorcet_implementations import (
    Copeland, MiniMaxMarginsSmith, MiniMaxWinningVotesSmith)
from src.election.condorcet.condorcet_no_winner_evaluations import SchulzeEvaluation, SmithEvaluation, SmithFastEvaluation, WeakCondorcetEvaluation
from src.election.election_authority import ElectionAuthority
from src.election.single_vote.single_vote_election_system import \
    SingleVoteElection
from src.election.trustee import Trustee
from src.protocols.protocol_suite import EmptyProtocolSuite, ProtocolSuite
from src.protocols.sublinear import SubLinearProtocolSuite
from src.util.point_vote import PointVote
from src.util.logging import setup_logging

log = logging.getLogger(__name__)


class CondorcetElectionTest(unittest.TestCase):

    def setUp(self):
        setup_logging()
        self.trustee_gen = lambda: PlainABB.gen_trustees(64, 5, 3, EmptyProtocolSuite)
        #self.trustee_gen = lambda: PaillierABB.gen_trustees(64, 5, 3, SubLinearProtocolSuite) #to run with Paillier
        self.startTime = time()

    def tearDown(self):
        t = time() - self.startTime
        log.info("%s: %.3f" % (self.id(), t))

    def test_condorcet_matrix_one(self):
        self._condorcet_one(ElectionAuthority(self.trustee_gen, Condorcet(4)))

    def test_condorcet_matrix_two(self):
        result = self._condorcet_two(ElectionAuthority(self.trustee_gen, Condorcet(4)))
        self.assertEqual(0, len(result))

    def test_condorcet_matrix_three(self):
        self._condorcet_three(ElectionAuthority(self.trustee_gen, Condorcet(4)))

    def test_condorcet_matrix_leak_one(self):
        self._condorcet_one(ElectionAuthority(self.trustee_gen, Condorcet(4, leak_better_half=False)))

    def test_condorcet_matrix_leak_two(self):
        result = self._condorcet_two(ElectionAuthority(self.trustee_gen, Condorcet(4, leak_better_half=False)))
        self.assertEqual(0, len(result))

    def test_condorcet_matrix_leak_three(self):
        self._condorcet_three(ElectionAuthority(self.trustee_gen, Condorcet(4, leak_better_half=False)))

    def test_condorcet_matrix_wikipedia(self):
        result = self._condorcet_wikipedia(ElectionAuthority(self.trustee_gen, Condorcet(4)))
        self.assertEqual(0, len(result))
        return result

    def test_minimax_margins(self):
        result = self._condorcet_wikipedia(ElectionAuthority(self.trustee_gen, MiniMaxMarginsSmith(4)))
        self.assertEqual(1, len(result))
        self.assertEqual(1, result[0])

    def test_minimax_winning_votes(self):
        result = self._condorcet_wikipedia(ElectionAuthority(self.trustee_gen, MiniMaxWinningVotesSmith(4)))
        self.assertEqual(1, len(result))
        self.assertEqual(0, result[0])

    def test_minimax_copeland(self):
        result = self._condorcet_wikipedia(ElectionAuthority(self.trustee_gen, Copeland(4)))
        self.assertEqual(3, len(result))
        self.assertTrue(0 in result)
        self.assertTrue(1 in result)
        self.assertTrue(2 in result)

    def test_minimax_copeland_leak(self):
        result = self._condorcet_wikipedia(ElectionAuthority(self.trustee_gen, Copeland(4, leak_max_points=True)))
        self.assertEqual(3, len(result))
        self.assertTrue(0 in result)
        self.assertTrue(1 in result)
        self.assertTrue(2 in result)

    def test_minimax_copeland_leak_borda(self):
        result = self._condorcet_wikipedia(ElectionAuthority(self.trustee_gen, Copeland(4, leak_better_half=True, leak_max_points=True)))
        self.assertEqual(3, len(result))
        self.assertTrue(0 in result)
        self.assertTrue(1 in result)
        self.assertTrue(2 in result)

    def test_weak_condorcet(self):
        result = self._condorcet_weak(ElectionAuthority(self.trustee_gen, Condorcet(4, [WeakCondorcetEvaluation])))
        self.assertEqual(1, len(result))
        self.assertTrue(0 in result)

    def test_schulze(self):
        result = self._condorcet_two(ElectionAuthority(self.trustee_gen, Condorcet(4, additional_evaluators=[SchulzeEvaluation])))
        self.assertEqual(2, len(result))
        self.assertTrue(0 in result)
        self.assertTrue(2 in result)

    def _condorcet_one(self, condorcet_system):
        condorcet_system.add_generic_vote(PointVote([4, 3, 2, 1]), count=0)
        condorcet_system.add_generic_vote(PointVote([1, 2, 3, 4]), count=1)
        condorcet_system.add_generic_vote(PointVote([1, 4, 3, 2]), count=2)
        condorcet_system.add_generic_vote(PointVote([3, 1, 4, 2]), count=3)
        result = condorcet_system.trigger_evaluation()
        self.assertEqual(1, len(result))
        self.assertEqual(2, result[0])

    def _condorcet_two(self, condorcet_system):
        condorcet_system.add_generic_vote(PointVote([4, 3, 2, 1]), count=3)
        condorcet_system.add_generic_vote(PointVote([1, 2, 3, 4]), count=1)
        condorcet_system.add_generic_vote(PointVote([1, 4, 3, 2]), count=1)
        condorcet_system.add_generic_vote(PointVote([3, 1, 4, 2]), count=2)
        return condorcet_system.trigger_evaluation()

    def _condorcet_three(self, condorcet_system):
        condorcet_system.add_generic_vote(PointVote([4, 3, 2, 1]), count=3)
        condorcet_system.add_generic_vote(PointVote([1, 2, 3, 4]), count=1)
        condorcet_system.add_generic_vote(PointVote([1, 4, 3, 2]), count=1)
        condorcet_system.add_generic_vote(PointVote([3, 1, 4, 2]), count=0)
        result = condorcet_system.trigger_evaluation()
        self.assertEqual(1, len(result))
        self.assertEqual(0, result[0])

    def _condorcet_weak(self, condorcet_system):
        condorcet_system.add_generic_vote(PointVote([4, 3, 2, 1]), count=3)
        condorcet_system.add_generic_vote(PointVote([1, 2, 3, 4]), count=1)
        condorcet_system.add_generic_vote(PointVote([1, 4, 3, 2]), count=1)
        condorcet_system.add_generic_vote(PointVote([3, 1, 4, 2]), count=1)
        return condorcet_system.trigger_evaluation()

    def _condorcet_wikipedia(self, condorcet_system):
        """https://en.wikipedia.org/wiki/Minimax_Condorcet_method"""
        condorcet_system.add_generic_vote(PointVote([4,2,3,1]), count=30)
        condorcet_system.add_generic_vote(PointVote([2,3,1,4]), count=15)
        condorcet_system.add_generic_vote(PointVote([1,3,2,4]), count=14)
        condorcet_system.add_generic_vote(PointVote([2,4,3,1]), count=6)
        condorcet_system.add_generic_vote(PointVote([1,1,3,5]), count=4)
        condorcet_system.add_generic_vote(PointVote([2,2,4,-1]), count=16)
        condorcet_system.add_generic_vote(PointVote([-1,4,3,-1]), count=14)
        condorcet_system.add_generic_vote(PointVote([3,-1,4,-1]), count=3)
        return condorcet_system.trigger_evaluation()
