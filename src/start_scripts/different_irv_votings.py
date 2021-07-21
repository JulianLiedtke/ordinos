import logging

from src.crypto.paillier_abb import PaillierABB
from src.election.election_authority import ElectionAuthority
from src.election.instant_runoff_voting.irv_election_system import (
    IRVElectionSystemAlternative, IRVElectionSystemNormal)
from src.protocols.sublinear import SubLinearProtocolSuite
from src.util.irv_util.irv_helper import bool_alternative
from src.util.logging import setup_logging
from src.util.position_vote import PositionVote

log = logging.getLogger(__name__)


def simulate_different_irv_votings(key_generator):
    # adjust election parameters here
    # one election per list entry will be executed
    num_cands = []
    num_votes = []
    sys_ids = []
    n_cand = 3

    for sys_id in range(0, 6):
        for voters in range(5, 11, 5):
            num_votes.append(voters)
            num_cands.append(n_cand)
            sys_ids.append(sys_id)

    votes = PositionVote.generate_random(max(num_votes), n_cand)

    # run elections and save running times in CSV-File
    while(len(sys_ids) > 0):
        num_cand = num_cands[0]
        num_vote = num_votes[0]
        sys_id = sys_ids[0]

        log.info('start election with the following parameters.')
        log.info('sys id:    {}'.format(sys_id))
        log.info('num cand:  {}'.format(num_cand))
        log.info('num votes: {}'.format(num_vote))


        alternative = bool_alternative(sys_id)
        election_system_class = None
        if not alternative:
            election_system = IRVElectionSystemNormal(num_cand, 16, sys_id)
        else:
            election_system = IRVElectionSystemAlternative(num_cand, 16, sys_id)
            
        ElectionAuthority(key_generator, election_system).add_votes_and_evaluate([votes[i] for i in range(num_vote)])

        del(num_cands[0])
        del(num_votes[0])
        del(sys_ids[0])


if __name__ == '__main__':
    setup_logging()

    simulate_different_irv_votings(lambda: PaillierABB.gen_trustees(64, 3, 2, SubLinearProtocolSuite))
