import logging

from src.election.evaluation.evaluation_protocol import EvaluationProtocol

log = logging.getLogger(__name__)


class PointThresholdEvaluation(EvaluationProtocol):
    """takes a dict cand->points and returns a list of all candidates with points >= point_limit"""

    def __init__(self, max_possible_points, point_limit):
        super().__init__()
        self.bits = None
        self.max_possible_points = max_possible_points
        self.point_limit = point_limit

    def run(self, votes):
        self.bits = self.abb.get_bits_for_size(self.max_possible_points)
        winners = []
        self.debug_cipher_list(log, 'Point limit election of: %s', votes)
        log.debug(self.point_limit)
        for cand in range(len(votes)):
            if self.abb.dec(self.abb.gt(votes[cand], self.point_limit, self.bits)):
                winners.append(cand)

        return winners
