from src.util.old_files.evaluator import Evaluator
import logging
from src.util.utils import init_empty_cand_dict

log = logging.getLogger(__name__)


class Former_ESystem():

    def __init__(self, num_candidates, num_servers, crypto, evaluator):
        self.crypto = crypto
        self.num_candidates = num_candidates
        self.init_votes()
        self.evaluator = evaluator

    def init_votes(self):
        """ inits a dictionary containing each candiate with 0 votes """
        self.votes = init_empty_cand_dict(self.num_candidates, self.crypto.encrypt(0))

    def addVote(self, vote):
        """ adds a vote by adding the ciphertexts to the current encrpyted votes """
        for cand in range(self.num_candidates):
            self.votes[cand] = self.crypto.add(self.votes[cand], vote[cand])

    def getResult(self):
        pass

    def getVotes(self):
        l = []
        for cand in range(self.num_candidates):
            l.append(self.votes[cand])
        return l

    def printVotes(self):
        for cand in range(self.num_candidates):
            log.info(str(cand) + ": " + str(self.votes[cand]))


    def init_evaluator(self):
        self.evaluator.set_num_candidates(self.num_candidates)
        self.evaluator.set_votes(self.votes)
        eq = lambda x, y: self.crypto.equality_test(x, y)
        self.evaluator.set_eq(eq)
        gt = lambda x, y: self.crypto.greater_than_test(x, y)
        self.evaluator.set_gt(gt)
        decrypt = lambda x: self.crypto.decrypt(x)
        self.evaluator.set_decryption(decrypt)
        enc_unified = lambda x: self.crypto.encrypt(x)
        self.evaluator.set_unified_encryption(enc_unified)
        add_func = lambda x, y: self.crypto.add(x, y)
        self.evaluator.set_add_func(add_func)
        mult_func = lambda x, y: self.crypto.mult(x, y)
        self.evaluator.set_mult_func(mult_func)
        enc_mult_func = lambda x, y: self.crypto.mult_ciphers(x, y)
        self.evaluator.set_enc_mult_func(enc_mult_func)
        sub_func = lambda x, y: self.crypto.sub(x, y)
        self.evaluator.set_sub_func(sub_func)

    def evaluate(self):
        self.init_evaluator()
        return self.evaluator.evaluate()

    def init_winner_eval(self):
        #initializes the OutputWinnerEvaluator for public elimination which returns the id of the "winner"
        #the "winner" (referred to Instant-Runoff-Voting) is the candidate that is eliminated in an iteration
        eval_winner = lambda cand : Former_ESystem(cand,cand,self.crypto,OutputWinnerEvaluator(self.crypto, False))
        self.evaluator.set_winner_eval(eval_winner)

    def init_secret_winner_eval(self):
        #initializes the OutputWinnerEvaluator for secret elimination which returns a vector that encrypts the "winner"
        #the vector has encrypted entries Enc(0) and exactly one entry Enc(1) for the eliminated candidate
        eval_winner = lambda cand: Former_ESystem(cand, cand, self.crypto, OutputWinnerEvaluator(self.crypto, True))
        self.evaluator.set_winner_eval(eval_winner)


class OutputWinnerEvaluator(Evaluator):
    def __init__(self, crypto, bool_secret):
        self.bool_secret = bool_secret
        self.proto = crypto.protocol
        if bool_secret:
            num_winner = self.proto.pk.encrypt(1, use_randomness=False)
        else:
            num_winner = 1

        import src.election.evaluation.simple_winner_evaluation
        self.new_proto = src.election.evaluation.simple_winner_evaluation.SimpleWinnerEvaluation(crypto.num_bits, num_winner, bool_secret)

    def evaluate(self):
        vector = self.proto.run_subprotocol(self.new_proto, [self.votes])
        if self.bool_secret:
            #set further Enc(1)-entries to Enc(0), this is necessary in case of a draw
            new_win_vector = []
            winner_found_inverted = self.encrypt_unified(1)
            #encrypted_two = self.encrypt_unified(2)
            for key in sorted(vector.keys()):
                new_result = self.enc_mult(winner_found_inverted, vector[key])
                new_win_vector.append(new_result)
                winner_found_inverted = self.sub(winner_found_inverted, new_result)
        else:
            #just take one candidate-id in case of a draw
            new_win_vector = vector[0]
        return new_win_vector
