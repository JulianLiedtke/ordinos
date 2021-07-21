
import logging
import math as m
import random
from time import time

from src.util.position_vote import PositionVote

log = logging.getLogger(__name__)


class PointVote(PositionVote):

    @staticmethod
    def generate_random_point_votes(n_votes, n_cand, min_points=0, max_points=10):
        """random votes by generating random points of each candidate between min_points and max_points
        || default min_points: 0|| default max_points: 10"""
        start_time = time()
        votes = [PointVote([random.randint(min_points, max_points) for j in range(n_cand)]) for i in range(n_votes)]
        log.info("Computation time to generate random votes: {}".format(time() - start_time))
        if n_votes <= 10:
            log.info("Generated votes: " + str(votes))
        return votes

    def __init__(self, point_list):
        """candidates with negative points will not get a position"""
        
        self.point_list = point_list

        # generate ranking list of candidates without equality, lower candidate
        # index is prefered
        sorted_points = point_list.copy()
        sorted_points.sort()
        sorted_points.reverse()

        position_list = []
        self.number_of_ignored = 0

        for cand in range(len(point_list)):
            points = point_list[cand]
            position = 0
            if points >= 0:
                position = sorted_points.index(points) + 1

            else:
                position = -1
                self.number_of_ignored += 1
            
            position_list.append(position)

        super().__init__(position_list)

    def get_points(self):
        """vote as list of points"""
        return self.point_list

    def __repr__(self):
        return "\026\n" + str(self.get_points())



class IllegalVoteException(Exception):
    pass
