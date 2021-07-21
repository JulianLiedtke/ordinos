from src.util.old_files.evaluator import Evaluator
import numpy as np
import logging

log = logging.getLogger(__name__)


class InstantRunoffEvaluator(Evaluator):
    """
    This evaluator contains functions needed for evaluation of an IRV-election
    """

    def evaluate(self):
        """return the candidate with the lowest number of votes by evaluation of the first row of the ballot"""
        sum_votes = []
        votes = self.get_votes()
        num_act_cand = np.size(votes[0][0])
        for cand in range(num_act_cand):
            #compute encrypted votes per candidate
            sum = self.encrypt_unified(0)
            for vote in votes:
                sum = self.add(sum, vote[0,cand])
            #"reverse" the number of votes to determine the loser instead of the winner
            sum_votes.append(self.sub(self.encrypt_unified(len(self.votes)), sum))
        evaluator = self.eval_winner(num_act_cand)
        evaluator.init_votes()
        evaluator.addVote(sum_votes)
        #call the OutputWinnerEvaluator
        return evaluator.evaluate()

    def set_winner_eval(self, eval_winner):
        #set the OutputWinnerEvaluator
        self.eval_winner_func = eval_winner

    def eval_winner(self, cand):
        return self.eval_winner_func(cand)

    def compute_ranking_vector(self):
        """calculate the ranking vector from the matrix for each voter as described in the elaboration"""
        rankings = []
        for vote in self.votes:
            ranking = []
            #multiply all matrix-entries by the increased index of the row ( = the belonging placement)
            mult_matrix = np.matrix([[self.mult(vote[i,j],i+1) for j in range(self.num_candidates)] for i in range(self.num_candidates)])

            #sum up the entries of the multiplied matrix in each column
            for col in range(self.num_candidates):
                sum = self.encrypt_unified(0)
                for row in range(self.num_candidates):
                    sum = self.add(sum, mult_matrix[row,col])
                ranking.append(sum)
            rankings.append(ranking)
        return rankings

    def compute_order_vector(self):
        """calculate the order vector from the matrix for each voter as described in the elaboration"""
        orders = []
        for vote in self.votes:
            order = []
            #multiply all matrix-entries by the increased index of the column ( = the belonging candidate-id)
            mult_matrix = np.matrix([[self.mult(vote[i,j], j+1) for j in range(self.num_candidates)] for i in range(self.num_candidates)])

            #sum up the entries of the multiplied matrix in each row
            for row in range(self.num_candidates):
                sum = self.encrypt_unified(0)
                for col in range(self.num_candidates):
                    sum = self.add(sum, mult_matrix[row,col])
                order.append(sum)
            orders.append(order)
        return orders

    def mult_matrix(self, first, second, num_rows):
        """multiply the entries of two matrices and return the result"""
        result = np.matrix([[None for i in range(len(first))] for j in range(len(first[0]))])
        for row in range(num_rows):
            for col in range(len(first[0])):
                result[row,col] = self.enc_mult(first[row,col],second[row,col])
        return result

    def exec_move_up(self, num_act_cand=None):
        """for each voter: move matrix-entries upwards to shift the "zero-row" at the very bottom"""
        votes = self.get_votes()
        num_col = np.size(votes[0][0])
        if num_act_cand is None:
            num_act_cand = num_col

        for vote in votes:
            for row in range(num_act_cand):
                #compute inverted sum of the row (sum_inv) that is an Enc(1) in case of the "zero-row"
                sum_row = self.encrypt_unified(0)
                for col in range(num_col):
                    sum_row = self.add(sum_row, vote[row, col])
                sum_inv = self.sub(self.encrypt_unified(1), sum_row)
                for col in range(num_col):
                    #an entry moves upwards if it is an encrypted one and the zero-row is above
                    product = self.enc_mult(sum_inv, vote[row + 1, col])
                    vote[row, col] = self.add(vote[row, col], product)
                    vote[row + 1, col] = self.sub(vote[row + 1, col], product)
        return votes

    def compute_counter(self, vote):
        """return encrypted pointer to the first row with sum of row != 0"""

        num_act_cand = np.size(vote[0])
        num_rows = self.num_candidates - num_act_cand

        #b is an encrypted bit, it saves the information whether the first row != 0 is already found
        b = self.encrypt_unified(0)
        counter = self.encrypt_unified(0)

        for row in range(num_rows):
            #compute inverted sum of the row
            sum = self.encrypt_unified(0)
            for cand in range(num_act_cand):
                sum = self.add(sum, vote[row, cand])
            inv_sum = self.sub(self.encrypt_unified(1), sum)

            if row == 0:
                #Henceforth: b = Enc(1) iff first row !=0 was not passed
                b = inv_sum
                counter = inv_sum
            else:
                #increase counter iff actual row = 0 and the first row != 0 was not passed at this time
                b = self.enc_mult(inv_sum, b)
                counter = self.add(counter, b)

        #increase counter to adapt counter to ranking (starts with one)
        counter = self.add(counter,self.encrypt_unified(1))
        return counter

    def compute_vote(self, ranking, counter):
        """ compute a new first preference from ranking and counter"""
        vote = []
        for rank in ranking:
            vote.append(self.abb.eq(rank, counter))
        return vote

    def evaluate_sum(self, sum_votes, num_act_cand):
        """ initialize and call the OutputWinnerEvaluator, return the result"""
        evaluator = self.eval_winner(num_act_cand)
        evaluator.init_votes()
        evaluator.addVote(sum_votes)
        return evaluator.evaluate()

    def evaluate_vector(self, votes):
        """return the candidate with the lowest number of votes for given ballots as vectors"""
        sum_votes = []
        num_act_cand = len(votes[0])

        for cand in range(num_act_cand):
            sum = self.encrypt_unified(0)
            for vote in votes:
                sum = self.add(sum, vote[cand])
            # "reverse" the number of votes to determine the loser instead of the winner
            sum_votes.append(self.sub(self.encrypt_unified(len(self.votes) + 1), sum))
        return self.evaluate_sum(sum_votes, num_act_cand)

    def evaluate_vector_secret(self, votes, eliminated):
        """
        firstly add votes for eliminated candidates so they do not lose again
        and then compute the candidate with the lowest number of votes. Afterwards reset votes to initial state.
        Use this method for secret elimination where votes for eliminated candidates cannot be discarded
        :param eliminated: vector that includes sufficiently
        many votes for eliminated candidates to avoid further eliminations
        """
        for cand in range(self.num_candidates):
            votes[0][cand] = self.add(votes[0][cand], eliminated[cand])

        res = self.evaluate_vector(votes)

        for cand in range(self.num_candidates):
            votes[0][cand] = self.sub(votes[0][cand], eliminated[cand])

        return res

    def compute_elimination_vector(self, order, loser):
        """compute elimination-vector from order-vector and the eliminated candidate.
        See written elaboration for further details """
        elimination_vector = []
        for cand in order:
            elimination_vector.append(self.abb.eq(cand, loser))
        return elimination_vector

    def compute_counter_secret(self, elimination, num_eliminations):
        """
        compute the counter (used for version with secret elimination)
        :param elimination: summed elimination vectors from different iterations (see elaboration)
        :param num_eliminations: number of candidates that are eliminated so far
        :return: the counter analogous to counter in public version (see "compute_counter")
        """

        counter = self.encrypt_unified(1)
        entry_found_inverted = self.encrypt_unified(1)
        #encrypted_two = self.encrypt_unified(2)
        for entry in range(num_eliminations):
            #increase counter iff only passed eliminated candidates and actual candidate was also already eliminated
            entry_found_inverted = self.enc_mult(entry_found_inverted, elimination[entry])
            counter = self.add(counter, entry_found_inverted)
        return counter

    def compute_new_tuples(self, new_elim):
        """
        compute updated tuples after each elimination, used in secret alternative version
        :param new_elim: vector with entries Enc(0) and one entry Enc(1) for the eliminated candidate
        """
        old_votes = self.votes
        new_votes = dict()

        for tuple in old_votes.keys():
            #get the equivalent tuples where one of the candidates is removed (all eligible updated tuples)
            for index in range(len(tuple)):
                cand = tuple[index]
                new_tuple = tuple[:index] + tuple[index+1:]
                if new_tuple not in new_votes:
                    new_votes[new_tuple] = self.encrypt_unified(0)
                #if the removed candidate was just eliminated, then the votes of the original tuple are added
                #otherwise no votes are added (product = 0)
                product = self.enc_mult(old_votes[tuple], new_elim[cand - 1])
                new_votes[new_tuple] = self.add(new_votes[new_tuple], product)
        return new_votes

    def decrypt_matrix_for_debug(self, matrix):
        """returns decrypted matrix if logging level is DEBUG, else []"""
        if log.getEffectiveLevel() > logging.DEBUG:
            return []

        return [[self.abb.dec(matrix[i, j]) for j in range(len(matrix[i]))] for i in range(len(matrix))]