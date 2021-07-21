import csv
import sys
from src.protocols.base_protocols import Protocol
from src.election.trustee import Trustee, init_trustees
from src.util.crypto.paillier_key_storage import KeyStorage
from time import sleep, time
from random import randint
from src.election.evaluation.seat_distribution import SeatDistributionProtocol
from src.election.evaluation.direct_mandate_eval import DirectMandateProtocol
import logging

log = logging.getLogger(__name__)

class FirstVote():
    """ set relevant parameters for the vote of direct mandates (candidates/constituencies/votes)
    pass an instance of this class to the "DirectMandateProtocol" to evaluate the result
    """

    def __init__(self, pk):
        self.constituencies = {}
        self.votes = {}
        self.cands = {}
        self.pk = pk

    def add_candiate(self, id, party_id, constituency):
        """ add a candidate belonging to a party and constituency
        nothing is done if id already belongs to an existing candidate or constituency does not exist
        """
        if id in self.cands:
            return False
        if constituency not in self.constituencies:
            return False

        self.cands[id] = (party_id, constituency)
        self.votes[id] = self.pk.encrypt(0, use_randomness=False)
        return True

    def get_candidates(self):
        return self.cands

    def add_vote(self, vote):
        """ add one vote (as a dict: cand-id -> encrypted value)
        skips cand-ids which do not refer to an exisiting candidate
        """
        for id, vote in vote.items():
            if id not in self.cands:
                continue
            self.votes[id] += vote

    def get_votes(self):
        return self.votes

    def add_random_votes(self, n):
        """ adds a random number of votes (between 0 and n) for each candidate """
        for cand in self.cands:
            rand_vote = randint(0, n)
            self.votes[cand] = self.pk.encrypt(rand_vote)

    def change_constituency(self, id, num_mandates):
        """ specify a new constituency by allocation of number of direct mandates or update an existing one """
        self.constituencies[id] = num_mandates

    def get_constituencies(self):
        return self.constituencies


class TwoVotesESystem():
    """ define relevant parameters for the parliamentary ballot and start the evaluation """

    def __init__(self, bits_key, bits_int, n_trustees, threshold, n_parties, secret_residual=False):
        """
        :param n_parties: number of competing parties
        :param secret_residual: pass "True" if secret version is required
        """
        self.bits_key = bits_key
        self.bits_int = bits_int
        self.threshold = threshold
        k = KeyStorage()
        self.pk, sk_shares = k.get_threshold_key(bits_key, n_trustees, threshold)
        self.n_parties = n_parties
        self.trustees = init_trustees(self.pk, sk_shares)
        self.init_votes()
        self.added_para = False
        self.secret_residual = secret_residual

    def init_votes(self):
        """ inits a dictionary containing each party with zero votes """
        self.second_votes = {}
        self.first_votes = {}

        for party in range(self.n_parties):
            # each party starts with 0 votes
            self.second_votes[party] = self.pk.encrypt(0)

    def add_second_vote(self, vote):
        """ adds a vote by adding the ciphertexts to the current encrypted votes """
        for party in range(self.n_parties):
            self.second_votes[party] += vote[party]

    def set_first_votes(self, vote):
        self.first_votes = vote

    def run(self):
        """ execute the three steps of the parliamentary ballot
        corresponding to written composition (three steps in chapter 3.2)
        """

        #execute first step (compute direct mandates)
        startTime = time()

        for t in self.trustees:
            proto_first = DirectMandateProtocol(self.bits_int)
            t.run_protocol(proto_first, self.first_votes)

        for t in self.trustees:
            while not t.is_protocol_finished():
                sleep(0.05)

        t = time() - startTime
        CSV_Writer_two_votes.set_time_first(t)

        winner_first_votes, first_votes = self.trustees[0].result

        #count direct mandates per party
        #and add party of successful candidates to clause_exclusions
        cands = first_votes.get_candidates()
        first_votes_party = {}
        for id in winner_first_votes:
            party = cands[id][0]
            if party in first_votes_party:
                first_votes_party[party] += 1
            else:
                first_votes_party[party] = 1
            if party not in self.clause_exclusions:
                self.clause_exclusions.append(party)

        #execute second step (compute unbalanced seat distribution)
        startTime = time()

        for t in self.trustees:
            proto_second = SeatDistributionProtocol(self.bits_int)
            if self.added_para:
                proto_second.set_num_seats(self.num_seats)
                proto_second.set_blocking(self.clause, self.clause_exclusions)
            if self.secret_residual:
                proto_second.set_residual_secret()

            t.run_protocol(proto_second, self.second_votes)

        for t in self.trustees:
            while not t.is_protocol_finished():
                sleep(0.05)

        t = time() - startTime
        CSV_Writer_two_votes.set_time_second(t)

        second_vote_result = self.trustees[0].result
        seats = second_vote_result[0]
        residual = second_vote_result[1]

        #print result of second step
        sum_seats = 0
        for party in range(self.n_parties):
            if party in seats:
                sum_seats += seats[party]

        #check if total number of seats was increased because of a draw
        #and add residual seats to the seat distribution
        #"residual" is an empty list in the secret version
        for party in residual:
            seats[party] += 1
        sum_seats += len(residual)
        if sum_seats != self.num_seats:
            self.num_seats = sum_seats

        #execute third step (compute balanced seat distribution)
        balance = self.balance(seats, first_votes_party, 1, True)

        return winner_first_votes, seats, residual, balance


    def add_random_second_votes(self, max, min=0):
        """ adds a random number of votes (between min and max) for each party """
        for party in range(self.n_parties):
            rand_vote = randint(min, max)
            log.info("Partei: " + str(party) + " Stimmen: " + str(rand_vote))
            self.second_votes[party] = self.pk.encrypt(rand_vote)

    def set_distribution_para(self, num_seats, clause, clause_exclusions):
        """
        :param num_seats: number of seats in parliament
        :param clause: number of required votes for a party to obtain seats
        :param clause_exclusions: ids of partys that are excluded from blocking clause (e.g. minorities)
        """
        self.num_seats = num_seats
        self.clause = clause
        self.clause_exclusions = clause_exclusions
        self.added_para = True

    def balance(self, seat_distribution, first_seats_party, factor, bool_compensation):
        """
        :param seat_distribution: unbalanced seat distribution
        :param first_seats_party: direct mandates per party
        :param factor: compensation factor f (see chapter 3.2)
        :param bool_compensation: True iff compensation of overhang seats should be realized
        :return: balanced seat distribution
        In the parliament, a party receives direct mandates AND number of seats from balanced seat distribution
        The function works exactly as described in chapter 3.2 without need of encrypted data/operations
        """
        balanced_seat_distribution = seat_distribution.copy()
        for party, first_seats in first_seats_party.items():
            balanced_seat_distribution[party] = round(balanced_seat_distribution[party] - factor*first_seats)

        if bool_compensation:
            max_overhang_factor = 0
            for party, new_seats in balanced_seat_distribution.items():
                if new_seats < 0:
                    overhang = new_seats * (-1)
                    overhang_factor = overhang / seat_distribution[party]
                    max_overhang_factor = max(max_overhang_factor, overhang_factor)
            for party in balanced_seat_distribution:
                seat_difference = round(seat_distribution[party] * max_overhang_factor)
                balanced_seat_distribution[party] += seat_difference

        else:
            for party in balanced_seat_distribution:
                balanced_seat_distribution[party] = max(balanced_seat_distribution[party], 0)

        return balanced_seat_distribution


class CSV_Writer_two_votes:
    """ This class is responsible for writing the measured times in CSV-files """
    csvfile = None
    writer = None
    time_first = 0
    time_second = 0
    fieldnames = []

    @classmethod
    def set_time_first(cls, time):
        """ set time of evaluation of direct mandates """
        log.info('First time: {:.3f}s'.format(time))
        cls.time_first = time

    @classmethod
    def set_time_second(cls, time):
        """ set time of computation of the seat distribution """
        log.info('Second time: {:.3f}s'.format(time))
        cls.time_second = time

    @classmethod
    def init_writer(cls):
        pass

    @classmethod
    def write(cls, sum_seats, num_parties, secret, failed_parties, residual):
        """
        write time-relevant parameters and times
        :param sum_seats: number of seats in parliament
        :param num_parties: number of competing parties
        :param secret: pass True iff secret version was executed, else False
        :param failed_parties: number of parties that failed on the blocking clause
        :param residual: were residual seats distributed? (pass False/True or "kA" for secret version)
        """
        cls.csvfile = open('times.csv', 'a', newline='')
        #cls.csvfile2 = open('Dropbox/Ergebnisse/times.csv', 'a', newline='')
        writer = csv.DictWriter(cls.csvfile, fieldnames=cls.fieldnames)
        #writer2 = csv.DictWriter(cls.csvfile2, fieldnames=cls.fieldnames)
        first = '%.2f' % (cls.time_first)
        second = '%.2f' % (cls.time_second)

        writer.writerow({cls.fieldnames[0]: sum_seats, cls.fieldnames[1]: num_parties,
                         cls.fieldnames[2]: secret,
                         cls.fieldnames[3]: failed_parties, cls.fieldnames[4]: residual,
                         cls.fieldnames[5]: first, cls.fieldnames[6]: second})
        #writer2.writerow({cls.fieldnames[0]: sum_seats, cls.fieldnames[1]: num_parties,
        #                 cls.fieldnames[2]: secret,
        #                 cls.fieldnames[3]: failed_parties, cls.fieldnames[4]: residual,
        #                 cls.fieldnames[5]: first, cls.fieldnames[6]: second})
        cls.csvfile.close()
        #cls.csvfile2.close()

        log.info("Succesfully written first time: " + str(first))
        log.info("Succesfully written second time: " + str(second))

    @classmethod
    def write_error(cls, info, comment):
        """ write the exception info if an exception occured """
        cls.csvfile = open('times.csv', 'a', newline='')
        #cls.csvfile2 = open('Dropbox/Ergebnisse/times.csv', 'a', newline='')
        writer = csv.DictWriter(cls.csvfile, fieldnames=cls.fieldnames)
        #writer2 = csv.DictWriter(cls.csvfile2, fieldnames=cls.fieldnames)

        writer.writerow({cls.fieldnames[0]: info[0], cls.fieldnames[1]: info[1], cls.fieldnames[2]: comment})
        #writer2.writerow({cls.fieldnames[0]: info[0], cls.fieldnames[1]: info[1], cls.fieldnames[2]: comment})
        cls.csvfile.close()
        #cls.csvfile2.close()
