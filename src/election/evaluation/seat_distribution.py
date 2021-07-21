import logging
import math

from src.election.evaluation.evaluation_protocol import EvaluationProtocol
from src.election.evaluation.simple_winner_evaluation import \
    SimpleWinnerEvaluation

log = logging.getLogger(__name__)


class SeatDistributionProtocol(EvaluationProtocol):
    """ Protocol for public and secret evaluation of the seat distribution """

    def __init__(self, bits):
        self.secret = False
        self.blocking_clause = 2000
        self.blocking_exclusions = []
        self.num_seats = 598
        self.bits = bits
        super().__init__()

    def set_blocking(self, num_min_votes, exclusions):
        """
        :param num_min_votes: required number of votes for passing the blocking clause
        :param exclusions: partys (e.g. minorities) that are excluded from blocking clause
        """
        self.blocking_clause = num_min_votes
        self.blocking_exclusions = exclusions

    def apply_blocking(self):
        """ remove parties which do not pass the blocking clause and corresponding votes """
        if self.blocking_clause is None:
            return
        new_votes = {}
        enc_clause = self.pk.encrypt(self.blocking_clause, use_randomness=False)
        for i, vote in self.votes.items():
            gt = self.abb.gt(vote, enc_clause, self.bits)
            dec_gt = self.abb.dec(gt)
            if dec_gt == 1 or i in self.blocking_exclusions:
                new_votes[i] = self.votes[i]
        self.votes = new_votes

    def set_num_seats(self, num_seats):
        self.num_seats = num_seats

    def compute_sum(self):
        """ call this procedure after applying the blocking
        to compute the encrypted sum of votes for parties that passed the blocking clause """
        sum_votes = self.abb.enc_zero
        for i, vote in self.votes.items():
            sum_votes += vote
        self.sum_votes = sum_votes
        log.info(self.abb.dec(self.sum_votes))

    def bin_search(self, number, lower, upper):
        """
        recursive binary search needed for the public version
        :param number = vote * num_seats (called "z" in 3.5.1)
        :return: the decrypted result (number of seats)
        """
        if lower == upper:
            self.num_assigned_seats += lower
            return lower

        #middle corresponds to "k" in 3.5.1
        middle = lower + math.ceil((upper - lower) / 2)
        log.info(middle)
        product_middle = self.sum_votes * middle

        gt = self.abb.gt(number, product_middle, self.bits)
        dec_gt = self.abb.dec(gt)
        if dec_gt == 0:
            return self.bin_search(number, lower, middle - 1)
        return self.bin_search(number, middle, upper)

    def compute_seats(self):
        """call the binary search and save the result (only public version)"""
        self.seats = {}
        for i, vote in self.votes.items():
            product = vote * self.num_seats
            self.seats[i] = self.bin_search(product, 0, self.num_seats)

    def compute_residuals(self):
        """ compute the values needed for computation of the residual seats
        the calculated residuals correspond to Enc(div_i) in 3.5.1 / 3.5.2 """
        self.residual = {}
        for i, vote in self.votes.items():
            product = vote * self.num_seats
            sub_product = self.sum_votes * self.seats[i]
            self.residual[i] = product - sub_product

    def run(self, votes):
        """
        run the evaluation of the seat distribution
        :return: the following tuple:
                    secret version: ( number of seats after both phases (see 3.4 Hare-Niemeyer) , [] )
                    public version: ( number of seats after phase 1 , list of parties receiving a residual seat )
        """
        if self.secret:
            self.num_assigned_seats = self.pk.encrypt(0, use_randomness=False)
        else:
            self.num_assigned_seats = 0

        self.votes = votes
        self.apply_blocking()
        self.compute_sum()

        if self.secret:
            self.compute_seats_secret()
        else:
            self.compute_seats()

        self.compute_residuals()

        num_seats = None
        if self.secret:
            num_seats = self.pk.encrypt(self.num_seats, use_randomness=False)
        else:
            num_seats = self.num_seats
        unassigned_seats = num_seats - self.num_assigned_seats

        residual_winners = None

        #compute residual seats
        if self.secret or unassigned_seats > 0:
            winner_elect = SimpleWinnerEvaluation(self.bits, unassigned_seats, self.secret)
            residual_winners = self.run_subprotocol(winner_elect, [self.residual])

        if not self.secret:
            return self.seats, residual_winners

        #secret version: add encrypted residual seats and decrypt the resulting sum
        decrypted_seats = {}
        for i, seats in self.seats.items():
            res_added = seats + residual_winners[i]
            dec_seats = self.abb.dec(res_added)
            decrypted_seats[i] = dec_seats
        return decrypted_seats, []

    def set_residual_secret(self):
        """ call if the secret version should be executed """
        self.secret = True

    def compute_seats_secret(self):
        """
        The alternative to the binary search. Needed for the secret version.
        :return: the encrypted result (number of seats)
        """
        self.seats = {}
        for i, vote in self.votes.items():
            product = vote * self.num_seats
            #log.info("Produkt: " + str(self.abb.dec(product)))
            gt_results = []
            #compute the r_k (see 3.5.2)
            for comp_seats in range(0, self.num_seats + 1):
                comp_product = self.sum_votes * comp_seats
                gt = self.abb.gt(product, comp_product, self.bits)
                #log.info("Test Sitze: " + str(comp_seats) + " Resultat: " + str(self.abb.dec(gt)))
                log.info("Test Sitze: " + str(comp_seats))
                gt_results.append(gt)

            #comute the rlambda_k and add them to the sum of k * rlambda_k (see 3.5.2)
            seats_counter = self.pk.encrypt(0, use_randomness=False)
            for num_seats in range(0, self.num_seats):
                reduced_result = gt_results[num_seats] - gt_results[num_seats + 1]
                seats = reduced_result * num_seats
                seats_counter = seats_counter + seats
            last = gt_results[self.num_seats] * self.num_seats
            seats_counter = seats_counter + last
            #log.info("Anzahl Sitze: " + str(self.abb.dec(seats_counter)))

            self.num_assigned_seats += seats_counter
            self.seats[i] = seats_counter
