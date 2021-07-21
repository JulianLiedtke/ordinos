import abc
import logging
from time import time

from src.election.trustee import Trustee, init_trustees
from src.util.csv_writer import CSV_Writer
from src.util.point_vote import IllegalVoteException
from src.util.protocol_runner import ProtocolRunner


class ElectionProperties(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, candidates, bulletin_board_functions_class, expected_votes_n=None, logger_name_extension=""):
        """candidates could either be the amount of cands or a list of names"""
        if isinstance(candidates, list):
            self.n_cand = len(candidates)
            self.candidate_names = candidates
        else:
            self.n_cand = candidates
            self.candidate_names = [i for i in range(self.n_cand)]
        self.system_name = str(self.__class__.__name__) + ("-" if logger_name_extension != "" else "") + logger_name_extension
        self.expected_votes_n = expected_votes_n
        self.bulletin_board_functions_class = bulletin_board_functions_class

    @abc.abstractmethod
    def get_evaluator(self, n_votes, abb):
        pass

    @abc.abstractmethod
    def generate_valid_vote(self, generic_vote, abb):
        pass
