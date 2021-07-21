import logging

from src.election.evaluation.evaluation_protocol import EvaluationProtocol
from src.election.evaluation.single_winner_evaluation import \
    SingleWinnerEvaluation

log = logging.getLogger(__name__)


class SimpleWinnerEvaluation(EvaluationProtocol):

    def __init__(self, bits, num_winners = 1, encrypted=False):
        self.num_winners = num_winners
        self.enc_threshold = encrypted
        self.bits = bits
        super().__init__()

    def run(self, votes):
        self.bits_for_candidates = self.abb.get_bits_for_size(len(votes))
        self.debug_cipher_list(log, 'Winner election of: %s', votes)
        if self.enc_threshold is False and self.num_winners == 1:
            return self.run_subprotocol(SingleWinnerEvaluation(pow(2, self.bits)), [votes])
        duel_matrix = self.create_duel_matrix(votes)
        if self.enc_threshold:
            num_votes = self.abb.enc_no_r(len(votes))
        else:
            num_votes = len(votes)
        threshold = num_votes - self.num_winners
        log.debug('Comparator: {}'.format(threshold))
        win_vec = self.create_wins_vector(duel_matrix)
        self.debug_cipher_list(log, 'wins: %s', win_vec)
        enc_winner = self.find_gt_candidates(win_vec, threshold, self.enc_threshold)
        if self.enc_threshold:
            return enc_winner

        indicator_winner = {}
        for i, val in enc_winner.items():
            indicator_winner[i] = self.abb.dec(val)
        winners = []
        for i, val in indicator_winner.items():
            if val == 1:
                winners.append(i)
        return winners

    def create_duel_matrix(self, votes):
        """ outputs a ranking matrix """
        matrix = {} 
        for i, a in votes.items():
            matrix[i] = {}
        for i, a in votes.items():
            for j, b in votes.items():
                if i == j:
                    matrix[i][j] = self.abb.enc_zero
                    matrix[j][i] = self.abb.enc_zero
                elif j < i:
                    gt = self.abb.gt(a, b, self.bits)
                    eq = self.abb.eq(a, b, self.bits)
                    matrix[i][j] = gt
                    matrix[j][i] = 1 - gt + eq
        return matrix

    def create_wins_vector(self, matrix):
        """ outputs a vector consisting of wins per candidate """
        wins_vec = {}
        for i, row in matrix.items():
            wins_vec[i] = self.abb.enc_zero
            for j, val in row.items():
                wins_vec[i] += val
        return wins_vec

    def find_gt_candidates(self, wins_vector, threshold_wins, encrypted=False):
        """ find all candidates which have at least threshold many wins """
        enc_cand_indicator = {}
        wins = threshold_wins
        enc_wins = None
        if encrypted:
            enc_wins = wins
        else:
            enc_wins = self.abb.enc_no_r(wins)
        for i, val in wins_vector.items():
            enc_cand_indicator[i] = self.abb.gt(val, enc_wins, self.bits_for_candidates)
        return enc_cand_indicator

    def find_lt_candidates(self, wins_vector, threshold_wins):
        """ find all candidates which have at most threshold many wins """
        enc_cand_indicator = {}
        wins = threshold_wins
        enc_wins = self.abb.enc_no_r(wins)
        for i, val in wins_vector.items():
            enc_cand_indicator[i] = self.abb.eq(val, enc_wins, self.bits_for_candidates) - self.abb.gt(val, enc_wins, self.bits_for_candidates) + 1
        return enc_cand_indicator

    def find_eq_candidates(self, wins_vector, threshold_wins):  
        """ find all candidates which have exactly threshold many wins """
        enc_cand_indicator = {}
        wins = threshold_wins
        enc_wins = self.abb.enc_no_r(wins)
        for i, val in wins_vector.items():
            enc_cand_indicator[i] = self.abb.eq(val, enc_wins, self.bits_for_candidates)
        return enc_cand_indicator
