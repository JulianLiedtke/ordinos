import logging
log = logging.getLogger(__name__)

def eliminate(system):
    """execute the elimination procedure, used for public version"""
    votes = system.getVotes()
    for tuple, value in votes.items():
        val = system.evaluator.decrypt(value)
        if val != 0:
            log.debug("Tupel " + str(tuple) + " entschlüsselte Anzahl: " + str(val))
    num_voter = system.get_num_voter()
    num_cand = len(list(votes.keys())[0])

    #compute votes per candidate
    zero = system.evaluator.encrypt_unified(0)
    votes_per_cand = [zero] * system.num_candidates
    for tuple, num_votes in votes.items():
        first = tuple[0]
        index = first - 1
        votes_per_cand[index] = system.evaluator.add(votes_per_cand[index], num_votes)

    #delete entries for eliminated candidates
    for cand in system.get_eliminated()[::-1]:
        index = cand - 1
        del(votes_per_cand[index])

    #"reverse" number of votes and determine the candidate with the fewest votes
    for i in range(num_cand):
        new_sum = system.evaluator.sub(system.evaluator.encrypt_unified(num_voter + 1), votes_per_cand[i])
        votes_per_cand[i] = new_sum
    loser = system.evaluator.evaluate_sum(votes_per_cand, num_cand)
    return loser


def run_irv_public(system):
    """run the public alternative IRV-version"""
    act_candidates = [i+1 for i in range(system.num_candidates)]

    while(True):
        log.debug('Starting round with candidates ' + str(act_candidates))

        loser = eliminate(system)
        loser_cand = act_candidates[loser]
        del(act_candidates[loser])

        if(len(act_candidates) == 1):
            log.debug('Winner is candidate ' + str(act_candidates[0]))
            return act_candidates[0]

        system.delete_entry(loser_cand)


def eliminate_secret(system, elim_add):
    """
    execute the elimination procedure, used for secret version
    :param elim_add: vector which includes votes for former eliminated candidates to avoid further eliminations
    :return: vector with entries Enc(0) and one entry Enc(1) for the eliminated candidate
    """
    votes = system.getVotes()
    for tuple, value in votes.items():
        val = system.evaluator.decrypt(value)
        if val != 0:
            log.debug("Tupel " + str(tuple) + " entschlüsselte Anzahl: " + str(val))
    num_voter = system.get_num_voter()

    #compute votes per candidate
    zero = system.evaluator.encrypt_unified(0)
    votes_per_cand = [zero] * system.num_candidates
    for tuple, num_votes in votes.items():
        first = tuple[0]
        index = first - 1
        votes_per_cand[index] = system.evaluator.add(votes_per_cand[index], num_votes)

    #add votes for eliminated candidates
    for i in range(len(elim_add)):
        votes_per_cand[i] = system.evaluator.add(votes_per_cand[i], elim_add[i])

    # "reverse" number of votes and compute the encrypted result-vector
    for i in range(system.num_candidates):
        new_sum = system.evaluator.sub(system.evaluator.encrypt_unified(num_voter + 1), votes_per_cand[i])
        votes_per_cand[i] = new_sum
    elimination = system.evaluator.evaluate_sum(votes_per_cand, system.num_candidates)
    return elimination


def run_irv_secret(system):
    """run the secret alternative IRV-version"""
    num_voter = system.get_num_voter()
    zero = system.evaluator.encrypt_unified(0)
    #elimination: Entry Enc(1) if candidate was eliminated in the past; Enc(0) else
    elimination = [zero] * system.num_candidates
    #elim_add: Entry Enc(num_voter + 1) if candidate was eliminated in the past; Enc(0) else
    elim_add = [zero] * system.num_candidates

    for iter in range(1, system.num_candidates):
        new_elim = eliminate_secret(system, elim_add)
        for e in range(len(elimination)):
            elimination[e] = system.evaluator.add(elimination[e], new_elim[e])

        if iter == system.num_candidates - 1:
            return compute_winner(system, elimination)

        for e in range(len(elim_add)):
            elim_add[e] = system.evaluator.mult(elimination[e], num_voter + 1)

        new_votes = system.evaluator.compute_new_tuples(new_elim)
        system.setVotes(new_votes)


def compute_winner(system, elimination):
    """return the winner of the irv-election in the end of the secret version"""
    log.debug("---------------------------------------------------")
    log.debug("Result: Winner has entry 0 ; Losers have entry 1")
    log.debug("---------------------------------------------------")
    winner = None
    for i in range(len(elimination)):
        result = system.evaluator.decrypt(elimination[i])
        if result == 0: winner = i+1
        log.debug("Candidate " + str(i+1) + " Result " + str(result))
    return winner
