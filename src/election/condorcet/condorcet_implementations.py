
from src.election.condorcet.condorcet_no_winner_evaluations import CopelandEvaluationFast, CopelandEvaluationSafe, MiniMaxMarginsEvaluation, MiniMaxWinningVotesEvaluation, SmithEvaluation, SmithFastEvaluation
from src.election.condorcet.condorcet_election_system import Condorcet

class MiniMaxMarginsSmith(Condorcet):
    def __init__(self, n_cand, leak_better_half=False, smith_leak_min_copeland=False):
        if smith_leak_min_copeland:
            super().__init__(n_cand, [SmithFastEvaluation, MiniMaxMarginsEvaluation], leak_better_half)
        else:
            super().__init__(n_cand, [SmithEvaluation, MiniMaxMarginsEvaluation], leak_better_half)

class MiniMaxWinningVotesSmith(Condorcet):
    def __init__(self, n_cand, leak_better_half=False, smith_leak_min_copeland=False):
        if smith_leak_min_copeland:
            super().__init__(n_cand, [SmithFastEvaluation, MiniMaxWinningVotesEvaluation], leak_better_half)
        else:
            super().__init__(n_cand, [SmithEvaluation, MiniMaxWinningVotesEvaluation], leak_better_half)

class Copeland(Condorcet):
    def __init__(self, n_cand, leak_better_half=False, leak_max_points=False, evaluate_condorcet=False):
        if leak_max_points:
            super().__init__(n_cand, [CopelandEvaluationFast], leak_better_half, evaluate_condorcet)
        else:
            super().__init__(n_cand, [CopelandEvaluationSafe], leak_better_half, evaluate_condorcet)