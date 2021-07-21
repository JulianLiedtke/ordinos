from src.util.old_files.evaluator import Evaluator
import logging

log = logging.getLogger(__name__)

class PlainSortingEvaluator(Evaluator):

    def evaluate(self):
        l = [i for i in range(self.get_num_candidates())]
        
        self.comparisons = 0
        
        l = self.insertionSort(l)
        
        winner = l[-1]

        log.info('Winner: Candidate ' + str(winner) + ' (' + str(self.comparisons) + ' comparisons)')

    def insertionSort(self, l):
        for i in range(1,len(l)):
            #element to be compared
            current = l[i]
            #comparing the current element with the sorted portion and swapping
            while i>0 and self.gt_plain(l[i-1], current) == 1:
                l[i] = l[i-1]
                i = i-1
                l[i] = current
        return l

    def gt_plain(self, x, y):
        self.comparisons += 1
        enc_votes_x = self.get_votes()[x]
        enc_votes_y = self.get_votes()[y]
        enc_gt = self.abb.gt(enc_votes_x, enc_votes_y)
        return self.abb.dec(enc_gt)