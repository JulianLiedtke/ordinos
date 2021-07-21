

import logging
from threading import Thread
from time import time

from src.election.bulletin_board.bulletin_board import BulletinBoard
from src.election.trustee import init_trustees
from src.protocols.sublinear import SubLinearProtocolSuite
from src.util.csv_writer import CSV_Writer
from src.util.point_vote import IllegalVoteException
from src.util.protocol_runner import ProtocolRunner


class ElectionAuthority():

    def __init__(self, trustee_gen, election_properties):
        trustees = trustee_gen()
        self.abb = trustees[0].abb.create_local_abb()
        self.abb_log = trustees[0].abb.op_logger

        self.n_cand = election_properties.n_cand
        self.candidate_names = election_properties.candidate_names
        self.n_votes = 0
        self.expected_votes_n = election_properties.expected_votes_n
        self.vote_transformation_time = 0

        self.bulletin_board = BulletinBoard(election_properties.bulletin_board_functions_class(), self.abb, self.n_cand)
        self.evaluation = ProtocolRunner(trustees, lambda: election_properties.get_evaluator(self.n_votes, self.abb))
        self.generate_encrypted_vote = election_properties.generate_valid_vote
        self.election_system_name = election_properties.system_name
        self.logger = logging.getLogger(self.election_system_name)

    def add_votes_and_evaluate(self, votes):
        """
        send votes to the bulletin board and evaluate
        """
        valid_votes = self.__transform_votes(votes)
        self.__add_votes_to_bulletin_board(valid_votes)
        return self.trigger_evaluation()

    def add_generic_vote(self, vote, count=1):
        """
        send a vote to the bulletin board
        | vote could be added more than once, which could be specified by count
        """
        valid_votes = self.__transform_votes([vote]*count)
        self.__add_votes_to_bulletin_board(valid_votes)

    def __add_votes_to_bulletin_board(self, valid_votes):
        for valid_vote in valid_votes:
            if self.expected_votes_n != None and self.n_votes + 1 > self.expected_votes_n:
                self.logger.warning("Maximum number (" + str(self.expected_votes_n) + ") of votes reached. Vote couldn't be added.")
            else:
                self.bulletin_board.add_vote(valid_vote)
                self.n_votes += 1

    def __transform_votes(self, generic_votes):
        start_time = time()

        valid_votes = []
        for vote in generic_votes:
            try:
                valid_vote = self.generate_encrypted_vote(vote, self.abb)
                valid_votes.append(valid_vote)
            except IllegalVoteException as e:
                self.logger.warning(str(vote) + " could't be added, because " + str(e))
        
        self.vote_transformation_time += time() - start_time
        return valid_votes

    def trigger_evaluation(self):
        self.logger.info('Computation time to transform votes: {:.3f}s'.format(self.vote_transformation_time))
        votes, vote_aggregation, aggregation_time = self.bulletin_board.get_votes()
        self.logger.info('Computation time to aggregate votes: {:.3f}s'.format(aggregation_time))
        CSV_Writer.set_eval_time(aggregation_time)

        if self.n_votes == 0:
            self.logger.warning("Election couldn't be started, because no valid vote was added")
            return

        if self.expected_votes_n and self.n_votes != self.expected_votes_n:
            self.logger.warning("Election expected " + str(self.expected_votes_n) + ", but got " + str(self.n_votes) + " votes")

        self.logger.info("Start evaluation")

        startTime = time()
        result, eval_prot = self.evaluation.run([vote_aggregation])

        if result == -1 or result == 'Abort.':
            self.logger.error("Something went wrong in evaluation.")
            raise ValueError("Something went wrong in evaluation.")

        # find real winner name
        winner_names = []
        for cand_index in result:
            winner_names.append(self.candidate_names[cand_index])

        self.logger.info('Result: {}'.format(winner_names))

        t = time() - startTime
        gt_ops = self.abb_log.get_count_gt_operations()
        eq_ops = self.abb_log.get_count_eq_operations()
        dec_ops = self.abb_log.get_count_dec_operations()
        mul_ops = self.abb_log.get_count_mul_operations()
        self.logger.info('Computation time to evaluate winner: {:.3f}s, with {} gt-ops, {} eq-ops, {} dec-ops and {} mul-ops'.format(t, gt_ops, eq_ops, dec_ops, mul_ops))
        CSV_Writer.set_eval_time(t)
        CSV_Writer.write_with_election_params(self.n_cand, self.n_votes, self.election_system_name, winner_names, gt_ops, eq_ops, dec_ops, mul_ops)

        return result
