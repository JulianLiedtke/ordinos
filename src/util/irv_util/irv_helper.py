from src.election.instant_runoff_voting.e_system_tuple import ESystemTuple
from src.election.instant_runoff_voting.e_system_matrix import ESystemMatrix
from src.election.instant_runoff_voting.irv_methods import run_system, run_system_counter, run_system_counter_secret, run_system_secret
from src.election.instant_runoff_voting.irv_alternative_methods import run_irv_public, run_irv_secret
from src.election.evaluation.instant_runoff_evaluator import InstantRunoffEvaluator
from itertools import permutations
import numpy as np
import logging

def prepare_irv(crypto, votes, secret_elim, alternative):
    """
    :param crypto: gives access to crypto protocols
    :param secret_elim: boolean, true for secret elimination
    :param alternative: boolean, true iff alternative (tuple) evaluation should be executed
    :return: the election system (Instance of ESystemMatrix or ESystemTuple)
    """

    system = None
    if alternative:
        num_cand = len(list(votes[0].keys())[0])
        system = ESystemTuple(num_cand, num_cand, crypto, InstantRunoffEvaluator())
    else:
        num_cand = np.size(votes[0][0])
        system = ESystemMatrix(num_cand, num_cand, crypto, InstantRunoffEvaluator())

    system.init_votes()
    system.init_evaluator()
    if secret_elim:
        system.init_secret_winner_eval()
    else:
        system.init_winner_eval()
    for vote in votes:
        system.addVote(vote)

    return system


#the evaluation procedures are represented by integers (0-5)
#bool_alternative returns true for alternative (tuple) procedures (4/5)
#bool_secret returns true for procedures with secret elimination (2/3/5)
#get_function returns the procedure
def bool_alternative(id):
    if id == 4 or id == 5:
        return True
    return False
def get_function(id):
    if id == 0:
        return run_system
    if id == 1:
        return run_system_counter
    if id == 2:
        return run_system_secret
    if id == 4:
        return run_irv_public
    if id == 5:
        return run_irv_secret
    return run_system_counter_secret

def bool_secret(id):
    if id == 0 or id == 1:
        return False
    if id == 4:
        return False
    return True
