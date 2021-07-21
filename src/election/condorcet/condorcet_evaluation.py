import logging
import math as m

from src.election.evaluation.evaluation_protocol import EvaluationProtocol
from src.election.evaluation.point_limit_evaluation import PointThresholdEvaluation

log = logging.getLogger(__name__)


class CondorcetEvaluation(EvaluationProtocol):

    def __init__(self, n_votes, additional_evaluators=None, leak_better_half=False, evaluate_condorcet=True):
        super().__init__()
        self.bits_compare = None
        self.n_votes = n_votes
        self.additional_evaluators = additional_evaluators
        self.leak_better_half = leak_better_half
        self.evaluate_condorcet = evaluate_condorcet

    def run(self, vote_aggregation):
        self.bits_compare = self.abb.get_bits_for_size(self.n_votes)
        self.matrix = vote_aggregation[0]
        self.n_cand = len(self.matrix)
        self.strong_gt_matrix = [[None for j in range(self.n_cand)] for i in range(self.n_cand)]
        self.strong_gt_sums = [self.abb.enc_zero for i in range(self.n_cand)]
        self.weak_gt_sums = [self.abb.enc_zero for i in range(self.n_cand)]

        self.debug_array_matrix(log, "Start Evaluation with Condorcet-Matrix: %s", self.matrix)

        self.handled_cands = []

        possible_winner = []
        # https://www.wahlrecht.de/lexikon/borda.html: optimization: condorcet winner should have average borda points
        if self.leak_better_half:
            average_borda_points = self.n_cand + 1
            possible_winner = self.run_subprotocol(PointThresholdEvaluation(self.n_cand * self.n_votes * 2, self.abb.enc_no_r(int(m.floor(average_borda_points * self.n_votes)))), [vote_aggregation[1]])
        else:
            possible_winner = [i for i in range(self.n_cand)]

        log.debug('possible winners: %s' % str(possible_winner))
        possible_winner = self.check_candidates(possible_winner, self.evaluate_condorcet)
        if len(possible_winner) == 1:
            return possible_winner
        
        if self.additional_evaluators is None or len(self.additional_evaluators) == 0:
            return []

        possible_winner = [i for i in range(self.n_cand)]
        if self.leak_better_half:
            # add other candidates for additional evaluation
            self.check_candidates([i for i in range(self.n_cand)], False)

        for evaluator_class in self.additional_evaluators:
            self.debug_array_matrix(log, 'strong_gt_matrix : %s', self.strong_gt_matrix)
            self.debug_cipher_list(log, 'weak_gt_sums: %s', self.weak_gt_sums)
            log.debug('Evaluator ' + evaluator_class.__name__ + ' will run with candidates ' + str(possible_winner))
            possible_winner = self.run_subprotocol (evaluator_class(),
                [self.n_votes, self.matrix, self.strong_gt_matrix, self.strong_gt_sums, self.weak_gt_sums, possible_winner])
            if len(possible_winner) == 1:
                return possible_winner
            # if possible winner empty
        
        return possible_winner

    def check_candidates(self, list, search_for_winner):
        new_candidates = list.copy()
        for cand in self.handled_cands:
            if cand in new_candidates:
                new_candidates.remove(cand)
        candidates_to_compare = new_candidates.copy()
        candidates_to_compare.extend(self.handled_cands)
        log.debug("new_candidates: %s" % str(new_candidates))
        log.debug("candidates_to_compare: %s" % str(candidates_to_compare))

        for i in range(len(new_candidates)):
            cand_a = new_candidates[i]
            for j in range(i+1, len(candidates_to_compare)):
                cand_b = candidates_to_compare[j]
                weak_gt = self.abb.gt(self.matrix[cand_a][cand_b], self.matrix[cand_b][cand_a], self.bits_compare)
                eq = self.abb.eq(self.matrix[cand_a][cand_b], self.matrix[cand_b][cand_a], self.bits_compare)
                strong_gt = weak_gt - eq
                self.strong_gt_matrix[cand_a][cand_b] = strong_gt
                self.strong_gt_matrix[cand_b][cand_a] = self.abb.enc_one - weak_gt
                self.weak_gt_sums[cand_a] += weak_gt
                self.weak_gt_sums[cand_b] += self.abb.enc_one - strong_gt
                self.strong_gt_sums[cand_a] += strong_gt
                self.strong_gt_sums[cand_b] += self.abb.enc_one - weak_gt

            self.debug_cipher_list(log, '%s', self.strong_gt_sums)
            # check if cand wins all duels
            if search_for_winner and self.abb.dec(self.abb.eq(self.strong_gt_sums[cand_a], len(candidates_to_compare) - 1, self.abb.get_bits_for_size(self.n_cand))) == 1:
                log.info('Needed %s iterations' % (i+1))
                return [cand_a]

        self.handled_cands.extend(new_candidates)
        return []
