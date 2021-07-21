import sys
import threading
import time

from src.election.evaluation.evaluation_protocol import EvaluationProtocol
from src.util.irv_util.irv_helper import *
from src.util.old_files.crypto_wrapper import Cryptodata


class IrvEvaluation(EvaluationProtocol):

    lock_writer = threading.Lock()

    def __init__(self, bits, system_id=0):
        #the system-id defines the chosen version
        super().__init__()
        self.system_id = system_id
        self.bits = bits

    def run(self, votes):
        crypto = Cryptodata(self, self.pk, self.bits)
        eval_algo = get_function(self.system_id)
        bool = bool_secret(self.system_id)
        bool_alt = bool_alternative(self.system_id)

        system = None
        #prepare the irv (initialize system and add the given votes)
        startTime = time.time()
        try:
            system = prepare_irv(crypto, votes, secret_elim=bool, alternative=bool_alt)
        except:
            endTime = time.time()
            exc_info = sys.exc_info()
            IrvEvaluation.lock_writer.acquire()
            IrvEvaluation.lock_writer.release()
            differTime = endTime - startTime
            raise

        #save runtime of preparation
        endTime = time.time()
        differTime = endTime - startTime

        result = None
        #evaluate the election result
        startTime = time.time()
        try:
            result = eval_algo(system)
        except:
            endTime = time.time()
            exc_info = sys.exc_info()
            IrvEvaluation.lock_writer.acquire()
            IrvEvaluation.lock_writer.release()
            differTime = endTime - startTime
            raise

        #save runtime of evaluation, return the winner
        endTime = time.time()
        differTime = endTime - startTime

        return [result - 1] # to have result like other systems
