import json
import logging
import math
import time
import unittest
from time import sleep, time

from src.crypto.plain_abb import PlainABB
from src.election.borda.borda_election_system import Borda
from src.election.borda.borda_implementations import EscElection, FisWorldCup
from src.election.election_authority import ElectionAuthority
from src.election.single_vote.single_vote_election_system import \
    SingleVoteElection
from src.protocols.protocol_suite import EmptyProtocolSuite
from src.util.point_vote import PointVote
from src.util.logging import setup_logging

log = logging.getLogger(__name__)


class BordaElectionTest(unittest.TestCase):

    def setUp(self):
        setup_logging()
        self.trustee_gen = lambda: PlainABB.gen_trustees(64, 5, 3, EmptyProtocolSuite)
        self.startTime = time()

    def tearDown(self):
        t = time() - self.startTime
        log.info("%s: %.3f" % (self.id(), t))

    def test_borda(self):
        e = self._init_election(4)
        e.add_generic_vote(PointVote([4, 3, 2, 1]), count=0)
        e.add_generic_vote(PointVote([1, 2, 3, 4]), count=1)
        e.add_generic_vote(PointVote([1, 4, 3, 2]), count=2)
        e.add_generic_vote(PointVote([3, 1, 4, 2]), count=3)
        result = e.trigger_evaluation()
        self.assertEqual(2, result[0])

    def test_borda_tie(self):
        e = self._init_election(4)
        e.add_generic_vote(PointVote([4, 3, 2, 1]), count=3)
        e.add_generic_vote(PointVote([1, 2, 3, 4]), count=1)
        e.add_generic_vote(PointVote([1, 4, 3, 2]), count=1)
        e.add_generic_vote(PointVote([3, 1, 4, 2]), count=2)
        result = e.trigger_evaluation()
        self.assertEqual(2, len(result))
        self.assertTrue(0 in result)
        self.assertTrue(2 in result)

    def _init_election(self, n_cand):
        return ElectionAuthority(self.trustee_gen, Borda(n_cand))
