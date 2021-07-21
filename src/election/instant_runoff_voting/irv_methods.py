import logging
import numpy as np
log = logging.getLogger(__name__)


def run_system(system):
    """run public version (without counter)"""
    log.debug("Decrypted votes (------> n_trustees prints per vote <------):")
    votes = system.getVotes()
    for vote in votes:
        log.debug(system.evaluator.decrypt_matrix_for_debug(vote))
        log.debug("------------------------------------------------")

    act_candidates = [i+1 for i in range(system.num_candidates)]

    while(True):
        log.debug('Starting round with candidates ' + str(act_candidates))

        loser = system.evaluator.evaluate()
        system.delete_column(loser)
        del(act_candidates[loser])

        if(np.size(system.getVotes()[0][0]) == 1):
            log.debug('Winner is candidate ' + str(act_candidates[0]))
            return act_candidates[0]

        new_votes = system.evaluator.exec_move_up()
        system.setVotes(new_votes)

def run_system_secret(system):
    """run secret version (without counter)"""
    log.debug("Decrypted votes (------> n_trustees prints per vote <------):")
    votes = system.getVotes()
    for vote in votes:
        log.debug(system.evaluator.decrypt_matrix_for_debug(vote))
        log.debug("------------------------------------------------")

    encrypted_zero = system.evaluator.encrypt_unified(0)
    #eliminated: Entry Enc(num_voter + 1) if candidate was eliminated in the past; Enc(0) else
    eliminated = [encrypted_zero for i in range(system.num_candidates)]
    #eliminated_bin: Entry Enc(1) if candidate was eliminated in the past; Enc(0) else
    eliminated_bin = [encrypted_zero for i in range(system.num_candidates)]
    for round in range(system.num_candidates):
        #get first row of the matrix from each voter
        first_rows = []
        votes = system.getVotes()
        for vote in votes:
            first_rows.append(vote[0])
        #determine the new loser
        act_eliminated = system.evaluator.evaluate_vector_secret(first_rows, eliminated)
        for cand in range(system.num_candidates):
            #update eliminated and eliminated_bin
            product = system.evaluator.mult(act_eliminated[cand], len(votes) + 1)
            eliminated_bin[cand] = system.evaluator.add(eliminated_bin[cand], act_eliminated[cand])
            eliminated[cand] = system.evaluator.add(eliminated[cand], product)


        if(round == system.num_candidates - 2):
            #compute and return the winner
            winner = None
            log.debug("---------------------------------------------------")
            log.debug("Result: Winner has entry 0 ; Losers have entry #Voter + 1")
            log.debug("---------------------------------------------------")
            for i in range(system.num_candidates):
                result = system.evaluator.decrypt(eliminated[i])
                if result == 0: winner = i + 1
                log.debug("Candidate " + str(i + 1) + " Result " + str(result))
            return winner

        enc_one = system.evaluator.encrypt_unified(1)
        elim_inv = [system.evaluator.sub(enc_one, eliminated_bin[i])for i in range(system.num_candidates)]
        #elim_matrix has entry Enc(0) in columns which belong to eliminated candidates and Enc(1) in the other columns
        elim_matrix = np.matrix([elim_inv for i in range(system.num_candidates)])

        votes_eliminated = []
        num_rows = system.num_candidates - round
        for vote in votes:
            #multiply entry-wise by elim_matrix to set entries, which belong to the eliminated candidate, to Enc(0)
            new_elim = system.evaluator.mult_matrix(vote, elim_matrix, num_rows)
            votes_eliminated.append(new_elim)
        system.setVotes(votes_eliminated)
        new_votes = system.evaluator.exec_move_up(num_rows - 1)
        system.setVotes(new_votes)

def run_system_counter(system):
    """run public version with counter"""

    log.debug("Decrypted votes (------> n_trustees prints per vote <------):")
    votes = system.getVotes()
    for vote in votes:
        log.debug(system.evaluator.decrypt_matrix_for_debug(vote))
        log.debug("------------------------------------------------")

    act_candidates = [i+1 for i in range(system.num_candidates)]
    rankings = system.evaluator.compute_ranking_vector()
    counter = None

    while (True):
        if(np.size(system.getVotes()[0][0]) == 1):
            log.debug('Winner is candidate ' + str(act_candidates[0]))
            return act_candidates[0]

        log.debug('Starting round with candidates ' + str(act_candidates))
        ptr = 0
        votes = []
        for vote in system.getVotes():
            if len(act_candidates) == system.num_candidates:
                #just take first row of matrix -> no costs (possible in first iteration)
                act_vote = vote[0]
            else:
                #compute counter and new first preference (for each voter)
                counter = system.evaluator.compute_counter(vote)
                act_vote = system.evaluator.compute_vote(rankings[ptr], counter)
            votes.append(act_vote)
            ptr += 1

        loser = system.evaluator.evaluate_vector(votes)
        system.delete_column(loser)
        for ranking in rankings:
            del (ranking[loser])
        del (act_candidates[loser])



def run_system_counter_secret(system):
    """run secret version with counter"""
    log.debug("Decrypted votes (------> n_trustees prints per vote <------):")
    votes = system.getVotes()
    for vote in votes:
        log.debug(system.evaluator.decrypt_matrix_for_debug(vote))
        log.debug("------------------------------------------------")

    #rankings: entry of i-th index gives placement of i-th candidate (for one ballot)
    #orders: entry of i-th index gives i-th placed candidate (for one ballot)
    rankings = system.evaluator.compute_ranking_vector()
    orders = system.evaluator.compute_order_vector()

    encrypted_zero = system.evaluator.encrypt_unified(0)
    loser = None
    counter = None
    votes_matrix = system.getVotes()

    #eliminations: summed elimination vectors from different iterations, see elaboration (for each voter)
    eliminations = [[encrypted_zero for i in range(system.num_candidates)] for j in range(len(orders))]
    #eliminated: Entry Enc(num_voter + 1) if candidate was eliminated in the past; Enc(0) else
    eliminated = [encrypted_zero for i in range(system.num_candidates)]

    for round in range(system.num_candidates - 1):
        votes = []
        for ptr in range(len(orders)):
            if (round != 0):
                #compute elimination vector and counter and therewith the new first preference (for each voter)
                elimination_vector = system.evaluator.compute_elimination_vector(orders[ptr], loser)
                for entry in range(system.num_candidates):
                    eliminations[ptr][entry] = system.evaluator.add(eliminations[ptr][entry], elimination_vector[entry])
                counter = system.evaluator.compute_counter_secret(eliminations[ptr], round)
                act_vote = system.evaluator.compute_vote(rankings[ptr], counter)
            else:
                #just take first row of matrix -> no costs (possible in first iteration)
                act_vote = votes_matrix[ptr][0]

            votes.append(act_vote)



        act_eliminated = system.evaluator.evaluate_vector_secret(votes, eliminated)

        #update eliminated
        for cand in range(system.num_candidates):
            product = system.evaluator.mult(act_eliminated[cand], len(orders) + 1)
            eliminated[cand] = system.evaluator.add(eliminated[cand], product)

        #compute encrypted id of the eliminated candidate (loser)
        loser = system.evaluator.encrypt_unified(1)
        cand_id = 0
        for cand in act_eliminated:
            product = system.evaluator.mult(cand, cand_id)
            loser = system.evaluator.add(loser, product)
            cand_id += 1

    #compute and return the winner
    log.debug("---------------------------------------------------")
    log.debug("Result: Winner has entry 0 ; Losers have entry #Voter + 1")
    log.debug("---------------------------------------------------")
    winner = None
    for i in range(len(eliminated)):
        result = system.evaluator.decrypt(eliminated[i])
        if result == 0: winner = i+1
        log.debug("Candidate " + str(i+1) + " Result " + str(result))
    return winner

