import logging
import math

from src.election.evaluation.evaluation_protocol import EvaluationProtocol
from src.election.evaluation.simple_winner_evaluation import \
    SimpleWinnerEvaluation

log = logging.getLogger(__name__)


class ParliamentaryEvaluation(EvaluationProtocol):
    """ Protocol for public and secret_residual evaluation of the seat distribution """

    def __init__(self, n_votes, n_seats, secret_residual, clause):
        self.n_votes = n_votes
        self.n_seats = n_seats
        self.secret_residual = secret_residual
        self.clause = clause
        super().__init__()

    def apply_blocking(self):
        """ remove parties which do not pass the blocking clause and corresponding votes """
        if self.clause is None:
            return
        new_votes = {}
        enc_clause = self.abb.enc_no_r(self.clause)
        bits_int = self.abb.get_bits_for_size(self.n_votes)
        for i, party_aggregation in self.vote_aggregation.items():
            gt = self.abb.gt(party_aggregation, enc_clause, bits_int)
            dec_gt = self.abb.dec(gt)
            if dec_gt == 1:
                new_votes[i] = self.vote_aggregation[i]
        log.debug(str(len(self.vote_aggregation)-len(new_votes)) + " parties were blocked")
        self.vote_aggregation = new_votes

    def compute_sum(self):
        """ call this procedure after applying the blocking
        to compute the encrypted sum of votes for parties that passed the blocking clause """
        sum_votes = self.abb.enc_zero
        for i, vote in self.vote_aggregation.items():
            sum_votes += vote
        self.sum_votes = sum_votes
        log.debug(self.abb.dec(self.sum_votes))

    def bin_search(self, number, lower, upper):
        """
        recursive binary search needed for the public version
        :param number = vote * n_seats (called "z" in 3.5.1)
        :return: the decrypted result (number of seats)
        """
        if lower == upper:
            self.num_assigned_seats += lower
            return lower

        # middle corresponds to "k" in 3.5.1
        middle = lower + math.ceil((upper - lower) / 2)
        log.debug(middle)
        product_middle = self.sum_votes * middle
        bits_int = self.abb.get_bits_for_size(self.n_votes * self.n_seats)
        gt = self.abb.gt(number, product_middle, bits_int)
        dec_gt = self.abb.dec(gt)
        if dec_gt == 0:
            return self.bin_search(number, lower, middle - 1)
        return self.bin_search(number, middle, upper)

    def compute_seats(self):
        """call the binary search and save the result (only public version)"""
        self.seats = {}
        for i, vote in self.vote_aggregation.items():
            product = vote * self.n_seats
            self.seats[i] = self.bin_search(product, 0, self.n_seats)

    def compute_residuals(self):
        """ compute the values needed for computation of the residual seats
        the calculated residuals correspond to Enc(div_i) in 3.5.1 / 3.5.2 """
        self.residual = {}
        for i, vote in self.vote_aggregation.items():
            product = vote * self.n_seats
            sub_product = self.sum_votes * self.seats[i]
            self.residual[i] = product - sub_product

    def run(self, votes):
        """
        run the evaluation of the seat distribution
        :return: the following tuple:
                    secret_residual version: ( number of seats after both phases (see 3.4 Hare-Niemeyer) , [] )
                    public version: ( number of seats after phase 1 , list of parties receiving a residual seat )
        """
        self.debug_cipher_list(log, '%s', votes)
        if self.secret_residual:
            self.num_assigned_seats = self.abb.enc_zero
        else:
            self.num_assigned_seats = 0

        self.vote_aggregation = votes
        self.apply_blocking()
        self.compute_sum()

        if self.secret_residual:
            self.compute_seats_secret()
        else:
            self.compute_seats()

        self.compute_residuals()

        n_seats = None
        if self.secret_residual:
            n_seats = self.abb.enc_no_r(self.n_seats)
        else:
            n_seats = self.n_seats
        unassigned_seats = n_seats - self.num_assigned_seats

        residual_winners = None

        #compute residual seats
        if self.secret_residual or unassigned_seats > 0:
            bits_int = self.abb.get_bits_for_size(self.n_votes)
            winner_elect = SimpleWinnerEvaluation(bits_int, unassigned_seats, self.secret_residual)
            residual_winners = self.run_subprotocol(winner_elect, [self.residual])

        if not self.secret_residual:
            log.info(self.seats)
            log.info(residual_winners)
            return self.seats.keys()

        #secret_residual version: add encrypted residual seats and decrypt the resulting sum
        decrypted_seats = {}
        for i, seats in self.seats.items():
            res_added = seats + residual_winners[i]
            dec_seats = int(self.abb.dec(res_added))
            decrypted_seats[i] = dec_seats

        log.info(decrypted_seats)
        return decrypted_seats.keys()

    def compute_seats_secret(self):
        """
        The alternative to the binary search. Needed for the secret_residual version.
        :return: the encrypted result (number of seats)
        """
        self.seats = {}
        for i, vote in self.vote_aggregation.items():
            product = vote * self.n_seats
            gt_results = []
            #compute the r_k (see 3.5.2)
            for comp_seats in range(0, self.n_seats + 1):
                comp_product = self.sum_votes * comp_seats
                bits_int = self.abb.get_bits_for_size(self.n_votes * self.n_seats)
                gt = self.abb.gt(product, comp_product, bits_int)
                log.debug("Test Sitze: " + str(comp_seats))
                gt_results.append(gt)

            #comute the rlambda_k and add them to the sum of k * rlambda_k (see 3.5.2)
            seats_counter = self.abb.enc_zero
            for n_seats in range(0, self.n_seats):
                reduced_result = gt_results[n_seats] - gt_results[n_seats + 1]
                seats = reduced_result * n_seats
                seats_counter = seats_counter + seats
            last = gt_results[self.n_seats] * self.n_seats
            seats_counter = seats_counter + last
            self.debug_cipher(log, "Anzahl Sitze: %s", seats_counter)

            self.num_assigned_seats += seats_counter
            self.seats[i] = seats_counter
