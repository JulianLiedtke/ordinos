import logging

from src.election.two_votes.two_votes_e_system import (CSV_Writer_two_votes,
                                                       FirstVote,
                                                       TwoVotesESystem)
from src.util.logging import setup_logging

log = logging.getLogger(__name__)


def run_parliamentary_ballot():
    # set general parameters of Ordinos
    bits_int = 64
    bits_key = 2048
    n_trustees = 3
    threshold = 2

    def system(n_parties, secret): return TwoVotesESystem(
        bits_key, bits_int, n_trustees, threshold, n_parties, secret)
    CSV_Writer_two_votes.init_writer()

    for seats in [10, 20, 50, 100, 500, 1000]:
        for n_parties in range(2, 5):
            for secret in False, True:
                for many_votes in False, True:
                    e = system(n_parties, secret)

                    votes = FirstVote(e.pk)
                    # first votes, constituencies and candidates could be added here to enable evaluation of direct mandates
                    # in this test: no constituencies, so evaluation of direct mandates is skipped
                    e.set_first_votes(votes)

                    if(many_votes):
                        log.info("Starting test with many votes")
                        e.add_random_second_votes(10**9, 10**5)
                    else:
                        log.info("Starting test with small number of votes")
                        e.add_random_second_votes(300)

                    e.set_distribution_para(seats, 0, [])

                    result = e.run()
                    failed_parties = n_parties - len(result[1])
                    residual = "kA" if secret else bool(result[2])

                    CSV_Writer_two_votes.write(
                        seats, n_parties, secret, failed_parties, residual)


if __name__ == '__main__':
    setup_logging()

    run_parliamentary_ballot()
