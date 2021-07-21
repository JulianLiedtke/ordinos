import logging

import numpy

from src.election.condorcet.condorcet_bulletin_boards import \
    CondorcetBulletinBoard
from src.election.condorcet.condorcet_evaluation import CondorcetEvaluation
from src.election.election_properties import ElectionProperties
from src.election.condorcet.condorcet_bulletin_boards import CondorcetBulletinBoard
import logging
import math as m

log = logging.getLogger(__name__)


class Condorcet(ElectionProperties):

    def __init__(self, candidates, additional_evaluators=None, leak_better_half=False, evaluate_condorcet=True):
        """if leak_better_half is set True, the group of candidates, who get the half of borda points, will be computed
        if there is a winner, he has to be out of this group <<https://en.wikipedia.org/wiki/Nanson%27s_method>>"""
        super().__init__(candidates, CondorcetBulletinBoard, logger_name_extension=str(leak_better_half))
        self.additional_evaluators = additional_evaluators
        self.leak_better_half = leak_better_half
        self.evaluate_condorcet = evaluate_condorcet

    def get_evaluator(self, n_votes, abb):
        eval = CondorcetEvaluation(n_votes, self.additional_evaluators, self.leak_better_half, self.evaluate_condorcet)
        return eval

    def generate_valid_vote(self, generic_vote, abb):
        """ generate encrypted gt-matrix and borda points if optimization activated out of generic vote """

        gt_matrix_enc = [[abb.enc(e) for e in row] for row in generic_vote.get_duel_matrix()]

        borda_points_enc = []
        if (self.leak_better_half):
            borda_winner_points =  [i for i in range(self.n_cand, 0, -1)]

            doubled_borda_points = {}
            for position, candidates in generic_vote.get_ranking_map().items():
                points_to_devide = 0
                if position > 0:
                    for i in range(len(candidates)):
                        points_to_devide += borda_winner_points[position - 1 + i]
                    for cand in candidates:
                        doubled_borda_points[cand] = m.ceil(2*points_to_devide/len(candidates))
                else:
                    # -1 would mean the candidate is ignored and has same preference as all other
                    # the average of borda points will be given
                    for cand in candidates:
                        doubled_borda_points[cand] = self.n_cand + 1

            borda_points_enc = [abb.enc(doubled_borda_points[i]) for i in range(len(doubled_borda_points))]
        
        return [gt_matrix_enc, borda_points_enc]
