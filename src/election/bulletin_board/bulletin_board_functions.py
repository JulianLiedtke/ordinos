import abc
import logging
from time import time

log = logging.getLogger(__name__)


class EmptyBulletinBoardFunctions():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_initial_vote_aggregation(self, abb, n_cand):
        return []

    @abc.abstractmethod
    def aggregate_vote(self, vote_aggregation, new_vote):
        pass
