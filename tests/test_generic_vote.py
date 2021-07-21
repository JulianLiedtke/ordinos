
import unittest
from src.util.point_vote import PointVote
from src.util.position_vote import PositionVote
import numpy as np

class GenericVoteText(unittest.TestCase):

    def test_position_vote(self):
        pos_vote = PositionVote([3,0,1,4,2,4,-2])
        self.assertEqual(pos_vote.get_number_of_ignored(), 2)
        self.assertEqual(pos_vote.get_first_doubled_position(), 4)
        self.assertEqual(pos_vote.get_positions(), [3,0,1,4,2,4,-2])
        self.assertTrue(np.array_equal(pos_vote.get_duel_matrix(), [[0, 0, 0, 1, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]]))
        
        ranking = pos_vote.get_ranking_map()
        self.assertEqual(ranking[-1], [1, 6])
        self.assertEqual(ranking[1], [2])
        self.assertEqual(ranking[2], [4])
        self.assertEqual(ranking[3], [0])
        self.assertEqual(ranking[4], [3, 5])

        
        pos_vote_2 = PositionVote([2,3,1,0,-2])
        self.assertEqual(pos_vote_2.get_first_doubled_position(), -1)
        self.assertEqual(pos_vote_2.get_number_of_ignored(), 2)

    def test_point_vote(self):
        point_vote = PointVote([9,7,5,-1,5,9,-3,0])
        self.assertEqual(point_vote.get_number_of_ignored(), 2)
        self.assertEqual(point_vote.get_first_doubled_position(), 1)
        self.assertEqual(point_vote.get_points(), [9,7,5,-1,5,9,-3,0])
        self.assertEqual(point_vote.get_positions(), [1,3,4,-1,4,1,-1,6])
        self.assertTrue(np.array_equal(point_vote.get_duel_matrix(), [[0, 1, 1, 0, 1, 0, 0, 1], [0, 0, 1, 0, 1, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 1, 1, 0, 1, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]))
        
        ranking = point_vote.get_ranking_map()
        self.assertEqual(ranking[-1], [3, 6])
        self.assertEqual(ranking[1], [0, 5])
        self.assertEqual(ranking[2], [])
        self.assertEqual(ranking[3], [1])
        self.assertEqual(ranking[4], [2, 4])
        self.assertEqual(ranking[5], [])
        self.assertEqual(ranking[6], [7])


        point_vote_2 = PointVote([2,3,1,0,-2])
        self.assertEqual(point_vote_2.get_first_doubled_position(), -1)
        self.assertEqual(point_vote_2.get_number_of_ignored(), 1)