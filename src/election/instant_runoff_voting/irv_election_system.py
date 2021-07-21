import logging
import random
from itertools import permutations
from time import sleep, time

import numpy as np

from src.election.bulletin_board.vote_remember_bulletin_board import \
    VoteRememberBulletinBoardFunctions
from src.election.election_properties import ElectionProperties
from src.election.evaluation.irv_evaluation import IrvEvaluation
from src.util.point_vote import IllegalVoteException


class IRVElectionSystemNormal(ElectionProperties):

    def __init__(self, candidates, bits_int, sys_id):
        """only usable with sys_id 0 - 3"""
        super().__init__(candidates, VoteRememberBulletinBoardFunctions, logger_name_extension=str(sys_id))
        self.bits_int = bits_int
        self.system_id = sys_id

    def generate_valid_vote(self, generic_vote, abb):
        """ inits a dictionary containing each candidate with zero votes """
        if generic_vote.get_number_of_ignored() > 0:
            raise IllegalVoteException("Candidates couldn't be ignored")
        if generic_vote.get_first_doubled_position() > 0:
            raise IllegalVoteException("Candidates couldn't be ranked on same position")

        positions = generic_vote.get_positions()

        #generate empty matrix and fill it
        matrix = np.matrix([[abb.enc(0) for i in range(self.n_cand)] for i in range(self.n_cand)])
        for cand in range(self.n_cand):
            matrix[positions[cand] - 1, cand] = abb.enc(1)

        return matrix

    def get_evaluator(self, n_votes):
        return IrvEvaluation(self.bits_int, self.system_id)


class IRVElectionSystemAlternative(ElectionProperties):

    def __init__(self, candidates, VoteRememberBulletinBoardFunctions, bits_int, sys_id):
        """only usable with sys_id 4 or 5"""
        super().__init__(candidates, logger_name_extension=str(sys_id))
        self.system_id = sys_id
        self.bits_int = bits_int
        self.tuples = list(permutations(list(range(1, self.n_cand + 1))))

    def generate_valid_vote(self, generic_vote, abb):
        """!!!vote will not transformed into tupel, the tupel will be generated with random!!!"""
        #generate one random vote as dict: tuples -> Enc(0)/Enc(1)
        #exactly one tuple gets Enc(1)
        vote = dict()
        for tuple in self.tuples:
            vote[tuple] = abb.enc(0)
        index = random.randrange(len(self.tuples))
        rand_tuple = self.tuples[index]
        vote[rand_tuple] = abb.enc(1)

        return vote

    def get_evaluator(self, n_votes):
        return IrvEvaluation(self.bits_int, self.system_id)
