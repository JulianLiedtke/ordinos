from src.election.borda.borda_election_system import Borda

class EscElection(Borda):
    """https://de.wikipedia.org/wiki/Eurovision_Song_Contest"""
    def __init__(self, n_candidates):
        super().__init__(n_candidates, list_of_points=[12, 10, 8, 7, 6, 5, 4, 3, 2, 1], allow_less_cands=True)

class MedalTableSystem(Borda):
    """https://de.wikipedia.org/wiki/Medaillenspiegel"""
    def __init__(self, n_candidates, count_of_comptetions):
        list_of_points = [pow(count_of_comptetions + 1, 2) + 1, count_of_comptetions + 1, 1]
        super().__init__(n_candidates, list_of_points, expected_votes_n=count_of_comptetions)

class FisWorldCup(Borda):
    """https://de.wikipedia.org/wiki/FIS-Punktesystem"""
    def __init__(self, n_candidates, count_of_comptetions):
        list_of_points= [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        super().__init__(n_candidates, list_of_points, expected_votes_n=count_of_comptetions, allow_less_cands=True, allow_equality=True)