import logging

from src.election.evaluation.evaluation_protocol import EvaluationProtocol

log = logging.getLogger(__name__)


class SingleWinnerEvaluation(EvaluationProtocol):
    """takes a dict cand->points and returns a list of all candidates with the most points"""

    def __init__(self, max_possible_points):
        """max_possible_points is needed to calculate the bits of operations"""
        super().__init__()
        self.bits = None
        self.max_possible_points = max_possible_points

    def run(self, votes):
        self.bits = self.abb.get_bits_for_size(self.max_possible_points)

        value_list = votes
        if isinstance(votes, map):
            value_list = votes.values()
        max_points = self.get_maximum(value_list, self.bits)

        winners = []
        _, winning_indcator = self.match_points(value_list, max_points, self.bits)
        for cand in range(0, len(votes)):
            if self.abb.dec(winning_indcator[cand]) == 1:
                winners.append(cand)

        return winners