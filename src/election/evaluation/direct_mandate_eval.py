from src.election.evaluation.evaluation_protocol import EvaluationProtocol
from src.election.evaluation.simple_winner_evaluation import \
    SimpleWinnerEvaluation


class DirectMandateProtocol(EvaluationProtocol):

    def __init__(self, bits):
        super().__init__()
        self.bits = bits

    def run(self, first_votes):
        winners = []
        constituencies = first_votes.get_constituencies()
        votes = first_votes.get_votes()
        cands = first_votes.get_candidates()

        #one evaluation per constituency
        for const, num_winner in constituencies.items():
            reduced_votes = {}
            for cand, tuple in cands.items():
                if tuple[1] == const:
                    reduced_votes[cand] = votes[cand]

            winner_elect = SimpleWinnerEvaluation(self.bits, num_winner)
            wins = self.run_subprotocol(winner_elect, [reduced_votes])
            winners.extend(wins)
        return winners, first_votes
