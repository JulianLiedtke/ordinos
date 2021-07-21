import logging
import gmpy2 as gmpy

from src.protocols.protocol import Protocol

log = logging.getLogger(__name__)


class EvaluationProtocol(Protocol):

    def get_maximum(self, list, bits):
        if len(list) == 0:
            return None

        self.debug_cipher_list(log, 'search for maximum in %s', list)

        maximum = list[0]
        for i in range(1, len(list)):
                gt_indicator = self.abb.gt(list[i], maximum, bits)
                maximum = self.if_then_else_enc(gt_indicator, list[i], maximum)
                
        self.debug_cipher(log, 'maximum is: %s', maximum)

        return maximum

    def get_minimum(self, list, bits):
        if len(list) == 0:
            return None

        self.debug_cipher_list(log, 'search for minimum in %s', list)

        minimum = list[0]
        for i in range(1, len(list)):
            st_indicator = self.abb.gt(minimum, list[i], bits)
            minimum = self.if_then_else_enc(st_indicator, list[i], minimum)
            
        self.debug_cipher(log, 'minimum is: %s', minimum)

        return minimum

    def debug_cipher(self, logger, text, cipher):
        """logs decrypted cipher, decrypt is only called if log level is debug"""
        if log.getEffectiveLevel() > logging.DEBUG:
            return 
        
        if isinstance(cipher, (int, gmpy.mpz().__class__)):
            logger.debug(text % str(cipher))
        else:
            logger.debug(text % str(self.abb.dec(cipher)))

    def debug_cipher_list(self, logger, text, list):
        """logs decrypted list of cipher texts, decrypt is only called if log level is debug"""
        if log.getEffectiveLevel() > logging.DEBUG:
            return 
        if isinstance(list[0], (int, gmpy.mpz().__class__)):
            logger.debug(text % str([(list[i] if list[i] is not None else None) for i in range(len(list))]))
        else:
            logger.debug(text % str([(self.abb.dec(list[i]) if list[i] is not None else None) for i in range(len(list))]))

    def debug_array_matrix(self, logger, text, matrix):
        """logs decrypted matrix of cipher texts, decrypt is only called if log level is debug"""
        if log.getEffectiveLevel() > logging.DEBUG:
            return
        if isinstance(matrix[0][0], (int, gmpy.mpz().__class__)):
            logger.debug(text % str([[(matrix[i][j] if matrix[i][j] is not None else None) for j in range(len(matrix[i]))] for i in range(len(matrix))]))
        else:
            logger.debug(text % str([[(self.abb.dec(matrix[i][j]) if matrix[i][j] is not None else None) for j in range(len(matrix[i]))] for i in range(len(matrix))]))

    def aggregate_dicts(self, dict_a, dict_b):
        for key, value in dict_b.items():
            self.add_operations(dict_a, key, value)

        return dict_a

    def if_then_else_enc(self, cond, val_true, val_false):
        """
        A simple if then else branching with encrypted values and condition.
        Use utils method instead, if values aren't encrypted
        Inputs/Output:
        - cond (0 or 1, can be encrypted)
        - val_true (return if cond=1, can be encrypted)
        - val_false (return if cond=0, can be encrypted)
        """
        return (cond * val_true) + ((1 - cond) * val_false)

    def match_points(self, point_list, points_to_search_enc, bits):	
	        match_indicator_dict = {}	
	        match_sum = self.abb.enc_zero	
		
	        for cand in range(0, len(point_list)):	
	            match = self.abb.eq(point_list[cand], points_to_search_enc, bits)	
	            match_sum += match	
	            match_indicator_dict[cand] = match
		
	        return match_sum, match_indicator_dict
