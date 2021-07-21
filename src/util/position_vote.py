
from time import time
import random
import logging
import numpy

log = logging.getLogger(__name__)

class PositionVote(object):

    @staticmethod
    def generate_random(n_votes, n_cand):
        """every candidate gets unique position
        | if equality between candidates is wanted look for PointVote (a subclass of this) generation"""
        start_time = time()
        votes = []
        for _ in range(n_votes):
            random_order = [position_points + 1 for position_points in range(n_cand)]
            random.shuffle(random_order)
            votes.append(PositionVote(random_order))
        log.info("Computation time to generate random votes: {}".format(time() - start_time))
        if n_votes <= 10:
            log.info("Generated position votes: " + str(votes))
        return votes

    position_list = []
    n_cand = 0

    def __init__(self, position_list):
        """position have to be valid (there has to be a first; if 2 canidates are second, noone is third; ...)
        | [1,3,2] would mean, that cand A is first, C second and B third
        | positions 0 or smaller mean, that the candidate is ignored""" 
        self.position_list = position_list
        self.n_cand = len(self.position_list)

    def get_positions(self):
        """a list of positions, like in constructor"""
        return self.position_list

    number_of_ignored = None
    def get_number_of_ignored(self):
        if self.number_of_ignored is not None:
            return self.number_of_ignored
        
        self.number_of_ignored = 0
        for pos in self.position_list:
            if pos < 1:
                self.number_of_ignored += 1
        
        return self.number_of_ignored

    first_doubled_position = None
    def get_first_doubled_position(self):
        """returns the first position, which has two or more candidates
        | -1 if no position is doubled"""
        if self.first_doubled_position is not None:
            return self.first_doubled_position

        position_count = [0] * self.n_cand

        for pos in self.position_list:
            if pos > 0:
                position_count[pos-1] += 1

        self.first_doubled_position = -1
        for pos_minus_one in range(len(position_count)):
            if position_count[pos_minus_one] > 1:
                self.first_doubled_position = pos_minus_one + 1
                break

        return self.first_doubled_position

    ranking_map = None
    def get_ranking_map(self):
        """dict: position->candidates(list)
        | ignored candidates have all position -1"""
        if self.ranking_map is not None:
            return self.ranking_map
        
        self.ranking_map = {}

        # initialize
        self.ranking_map[-1] = []
        for pos_minus_one in range(self.n_cand):
            self.ranking_map[pos_minus_one + 1] = []

        # fill
        for cand_i in range(self.n_cand):
            position = self.position_list[cand_i]
            if position < 1:
                position = -1
            self.ranking_map[position].append(cand_i)

        return self.ranking_map

    def get_position(self, position):
        if self.ranking_map is not None:
            return self.ranking_map[position]

        cands = []

        for cand_i in range(self.n_cand):
            cand_position = self.position_list[cand_i]
            if cand_position == position:
                cands.append(cand_i)

        return cands

    duel_matrix = None
    def get_duel_matrix(self):
        """generate matrix (numpy array), which indicates who is prefered against whom
        | [[0,0,1],[0,0,1],[0,0,0]] means, that A and B win against C but A and B are equal"""
        if self.duel_matrix is not None:
            return self.duel_matrix

        self.duel_matrix = [[0 for _ in range(self.n_cand)] for _ in range(self.n_cand)]

        for i in range(self.n_cand):
            for j in range(i+1, self.n_cand):
                preferation = self.preferation(i, j)
                if preferation == 1:
                    self.duel_matrix[i][j] = 1
                elif preferation == -1:
                    self.duel_matrix[j][i] = 1

        return self.duel_matrix

    def preferation(self, cand_a, cand_b):
        """return 1 if cand_a > cand_b, 0 if cand_a = cand_b, -1 if cand_a < cand>b
        | if one of candidates is ignored (0 points), no preferation is possible => returns 0"""

        pos_a = self.position_list[cand_a]
        pos_b = self.position_list[cand_b]

        if pos_a < 1 or pos_b < 1: # check if one is ignored
            return 0
        
        if pos_a < pos_b:
            return 1
        elif pos_a > pos_b:
            return -1
        else:
            return 0

    def __repr__(self):
        return "\026\n" + str(self.position_list)
        