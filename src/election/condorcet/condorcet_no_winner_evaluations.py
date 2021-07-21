import logging

from src.election.evaluation.evaluation_protocol import EvaluationProtocol
from src.election.evaluation.single_winner_evaluation import \
    SingleWinnerEvaluation
from src.util.utils import init_empty_cand_dict

log = logging.getLogger(__name__)


class CopelandEvaluationFast(EvaluationProtocol):

    def run(self, max_points, original_matrix, strong_gt_matrix, strong_gt_sums, weak_gt_sums, possible_winner):
        copeland_points = []
        for cand in range(len(strong_gt_sums)):
            copeland_points.append(strong_gt_sums[cand] + weak_gt_sums[cand])

        highest_possible_win_count = (len(copeland_points)-1)*2
        bits = self.abb.get_bits_for_size(highest_possible_win_count)
        self.debug_cipher_list(log, '%s', copeland_points)
        for win_count in range(highest_possible_win_count, 0, -1):
            winners = []
            win_count_enc = self.abb.enc_no_r(win_count)
            for cand in possible_winner:
                if self.abb.dec(self.abb.eq(win_count_enc, copeland_points[cand], bits)) == 1:
                    winners.append(cand)

            if len(winners) > 0:
                log.info('LEAK: max copeland points = %s' % win_count)
                return winners
        return []


class CopelandEvaluationSafe(EvaluationProtocol):

    def run(self, max_points, original_matrix, strong_gt_matrix, strong_gt_sums, weak_gt_sums, possible_winner):
        copeland_points = []
        for cand in range(len(strong_gt_sums)):
            copeland_points.append(strong_gt_sums[cand] + weak_gt_sums[cand])
        return self.run_subprotocol(SingleWinnerEvaluation(max_points), [copeland_points])


class MiniMaxMarginsEvaluation(EvaluationProtocol):
    """ find candidate with the scarcest defeat: max(min([x,y]-[y,x]))
    | https://en.wikipedia.org/wiki/Minimax_Condorcet_method"""

    def run(self, max_points, original_matrix, strong_gt_matrix, strong_gt_sums, weak_gt_sums, possible_winner):
        bits = self.abb.get_bits_for_size(max_points)
        worst_results = []
        max_points_enc = self.abb.enc_no_r(max_points)

        for i in possible_winner:
            differences = []
            for j in possible_winner:
                if i == j:
                    continue
                defeat = original_matrix[j][i] - original_matrix[i][j]
                # important: ignore wins by using preference matrix, so no bigger bit number is needed
                differences.append(self.if_then_else_enc(strong_gt_matrix[i][j], max_points, max_points_enc - defeat))
            worst_results.append(self.get_minimum(differences, bits))

        return self.run_subprotocol(SingleWinnerEvaluation(max_points), [worst_results])


class MiniMaxWinningVotesEvaluation(EvaluationProtocol):
    """ find candidate with the least winner points when losed: max(min(x>=y ? max_points : max_points-y))
    | https://en.wikipedia.org/wiki/Minimax_Condorcet_method"""


    def run(self, max_points, original_matrix, strong_gt_matrix, strong_gt_sums, weak_gt_sums, possible_winner):
        bits = self.abb.get_bits_for_size(max_points)
        worst_results = []
        max_points_enc = self.abb.enc_no_r(max_points)

        for i in possible_winner:
            opponent_results_inverted = []
            for j in possible_winner:
                if i == j:
                    continue
                opponent = original_matrix[j][i]
                # important: ignore wins by using preference matrix, so condorcet criteria is fullfilled
                opponent_results_inverted.append(self.if_then_else_enc(strong_gt_matrix[i][j], max_points, max_points_enc - opponent))
            worst_results.append(self.get_minimum(opponent_results_inverted, bits))

        return self.run_subprotocol(SingleWinnerEvaluation(max_points), [worst_results])

class WeakCondorcetEvaluation(EvaluationProtocol):
    """ find candidate with the least winner points when losed: max(min(x>=y ? max_points : max_points-y))
    | https://en.wikipedia.org/wiki/Minimax_Condorcet_method"""


    def run(self, max_points, original_matrix, strong_gt_matrix, strong_gt_sums, weak_gt_sums, possible_winner):
        needed_wins_enc = self.abb.enc_no_r(len(original_matrix) - 1)

        winner = []
        for cand in range(len(original_matrix)):
            if self.abb.dec(self.abb.eq(weak_gt_sums[cand], needed_wins_enc, self.abb.get_bits_for_size(len(original_matrix)))) == 1:
                winner.append(cand)
        return winner

class SmithEvaluation(EvaluationProtocol):
    """searchs for the first SmithSet | https://electowiki.org/wiki/Smith_set"""

    def run(self, max_points, original_matrix, strong_gt_matrix, strong_gt_sums, weak_gt_sums, possible_winner):
        return self.smith_evaluation(strong_gt_sums, weak_gt_sums, possible_winner, False)

    def smith_evaluation(self, strong_gt_sums, weak_gt_sums, possible_winner, leak_min_copeland):
        n_cand = len(strong_gt_sums)
        copeland_points = []
        for cand in range(n_cand):
            copeland_points.append(strong_gt_sums[cand] + weak_gt_sums[cand])

        self.debug_cipher_list(log, 'copeland-points: %s', copeland_points)

        points_to_search = 2* (n_cand - 1)
        cand_count = self.abb.enc_zero
        point_sum = self.abb.enc_zero
        smith_set_indicator = init_empty_cand_dict(n_cand, self.abb.enc_zero)
        bits_to_compare = self.abb.get_bits_for_size(points_to_search) # maximum possible copeland points
        bits_to_check_cand_count = self.abb.get_bits_for_size(n_cand)
        bits_to_check_finished = self.abb.get_bits_for_size(n_cand*(n_cand-1))
        finished = self.abb.enc_zero

        while True:
            match_count, match_cand_indicator_dict = self.match_points(copeland_points, self.abb.enc_no_r(points_to_search), bits_to_compare)
            if leak_min_copeland:
                cand_count += match_count
                point_sum += match_count * points_to_search
            else:
                cand_count += match_count * (1-finished)
                point_sum += match_count * points_to_search * (1-finished)
            
            for cand, indicator in match_cand_indicator_dict.items():
                smith_set_indicator[cand] += indicator # every candidate could match only one time, so indicator is never bigger than 1
            self.debug_cipher_list(log, 'match indicator: %s', smith_set_indicator)
            self.debug_cipher(log, 'for %s points', points_to_search)

            finished = (1 - self.abb.eq(cand_count, self.abb.enc_zero, bits_to_check_cand_count)) * self.abb.eq(cand_count* (2*n_cand - 1 - cand_count), point_sum, bits_to_check_finished)
                
            if (leak_min_copeland) and self.abb.dec(finished) == 1:
                log.info('minimal copeland points: %s' % str(points_to_search))
                break

            if points_to_search == 1: #candidate with 0 points couldn't be part of Smith-Set
                if (leak_min_copeland):
                    log.warn("Something went wrong in smith set alg")
                    return []
                else:
                    break

            points_to_search -= 1
            
        smith_set = []
        for cand in possible_winner:
            if self.abb.dec(smith_set_indicator[cand]) == 1:
                smith_set.append(cand)

        return smith_set

class SmithFastEvaluation(SmithEvaluation):
    """searchs for the first SmithSet | https://electowiki.org/wiki/Smith_set"""

    def run(self, max_points, original_matrix, strong_gt_matrix, strong_gt_sums, weak_gt_sums, possible_winner):
        return self.smith_evaluation(strong_gt_sums, weak_gt_sums, possible_winner, True)

class SchulzeEvaluation(EvaluationProtocol):

    def run(self, max_points, original_matrix, strong_gt_matrix, strong_gt_sums, weak_gt_sums, possible_winner):
        bits_for_points = self.abb.get_bits_for_size(max_points*2)

        path = [[None for j in possible_winner] for i in possible_winner]
        for cand_a in possible_winner:
            for cand_b in possible_winner:
                if cand_a != cand_b:
                    path[cand_a][cand_b] = original_matrix[cand_a][cand_b] - original_matrix[cand_b][cand_a] + max_points

        
        for cand_a in possible_winner:
            for cand_b in possible_winner:
                if cand_a != cand_b:
                    for cand_c in possible_winner:
                        if cand_a != cand_c and cand_b != cand_c:
                            path[cand_b][cand_c] = self.get_maximum([path[cand_b][cand_c], 
                                self.get_minimum([path[cand_b][cand_a], path[cand_a][cand_c]], bits_for_points)], bits_for_points)

        self.debug_array_matrix(log, "Strongest-Path-Matrix: %s", path)

        duel_matrix = [[None for j in possible_winner] for i in possible_winner]
        for cand_a in possible_winner:
            for cand_b in possible_winner:
                if cand_a < cand_b:
                    gt = self.abb.gt(path[cand_a][cand_b], path[cand_b][cand_a], bits_for_points)
                    eq = self.abb.eq(path[cand_a][cand_b], path[cand_b][cand_a], bits_for_points)
                    duel_matrix[cand_a][cand_b] = gt
                    duel_matrix[cand_b][cand_a] = 1 - gt + eq
        
        self.debug_array_matrix(log, "Duel-Winner-Matrix: %s", duel_matrix)

        winners = []
        for cand_a in possible_winner:
            winning_sum = self.abb.enc_zero
            for cand_b in possible_winner:
                if cand_a != cand_b:
                    winning_sum += duel_matrix[cand_a][cand_b]
            winning_indicator = self.abb.eq(winning_sum, self.abb.enc_no_r(len(possible_winner)-1), self.abb.get_bits_for_size(len(possible_winner)-1))
            if self.abb.dec(winning_indicator) == 1:
                winners.append(cand_a)

        return winners
