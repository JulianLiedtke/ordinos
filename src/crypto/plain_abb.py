import logging
from math import log2
from random import randint

import numpy as np
from gmpy2 import mpz

from src.crypto.abb import ABB, Ciphertext
from src.protocols.protocol_suite import EmptyProtocolSuite
from src.util.primes import PrimeStorage

log = logging.getLogger(__name__)


class PlainABB(ABB):

    @classmethod
    def keygen(cls, bits, num_shares, threshold):
        """
        generates public and private key for the plain abb
        """
        pk = PublicPlainKey()
        sks = [SecretPlainKey(i, threshold) for i in range(num_shares)]
        return pk, sks

    def __init__(self, prot_suite, pk, num_shares, threshold, sk):
        super().__init__(prot_suite, pk, num_shares, threshold, sk)

    def init_cipher(self, val):
        return PlainCiphertext(self, val)

    def get_random_plaintext(self):
        """returns a possible plaintext"""
        return randint(0, 2*32)

    def enc_get_r(self, plain):
        cipher = PlainCiphertext(self, plain)
        r = 0
        return cipher, r

    def enc(self, plain):
        if not isinstance(plain, (int, mpz().__class__)):
            raise ValueError('{} is not a valid number (it is of type {}).'.format(plain, type(plain)))
        c, _ = self.enc_get_r(plain)
        return c

    def enc_no_r(self, plain):
        return self.enc(plain)

    def dec(self, cipher):
        return cipher.val

    def eq(self, input1, input2, bits):
        cipher1 = self.convert_to_cipher(input1)
        cipher2 = self.convert_to_cipher(input2)
        result = self.prot_suite.eq(cipher1, cipher2, bits)
        if result:
            return result

        if cipher1.val == cipher2.val:
            return self.enc(1)
        else:
            return self.enc(0)

    def gt(self, input1, input2, bits):
        cipher1 = self.convert_to_cipher(input1)
        cipher2 = self.convert_to_cipher(input2)
        result = self.prot_suite.gt(cipher1, cipher2, bits)
        if result:
            return result

        if cipher1.val >= cipher2.val:
            return self.enc(1)
        else:
            return self.enc(0)

    def randomize(self, cipher, r=None):
        return cipher

    def get_r(self):
        return 0

    def eval_add_protocol(self, cipher1, cipher2):
        val1 = None
        val2 = None
        if isinstance(cipher1, PlainCiphertext):
            val1 = cipher1.val
        else:
            val1 = cipher1
        if isinstance(cipher2, PlainCiphertext):
            val2 = cipher2.val
        else:
            val2 = cipher2

        s = val1 + val2
        return self.enc(s)

    def eval_sub_protocol(self, cipher1, cipher2):
        val1 = None
        val2 = None
        if isinstance(cipher1, PlainCiphertext):
            val1 = cipher1.val
        else:
            val1 = cipher1
        if isinstance(cipher2, PlainCiphertext):
            val2 = cipher2.val
        else:
            val2 = cipher2

        dif = val1 - val2
        return self.enc(dif)

    def eval_mul_protocol(self, cipher1, cipher2):
        if isinstance(cipher1, PlainCiphertext):
            if isinstance(cipher2, PlainCiphertext):
                result = self.prot_suite.mul(cipher1, cipher2)
                if result:
                    return result

        val1 = None
        val2 = None
        if isinstance(cipher1, PlainCiphertext):
            val1 = cipher1.val
        else:
            val1 = cipher1
        if isinstance(cipher2, PlainCiphertext):
            val2 = cipher2.val
        else:
            val2 = cipher2

        prod = val1 * val2
        return self.enc(prod)


class PlainKeyStorage():

    def __init__(self):
        pass

    def get_threshold_key(self, bits_key, n_parties, threshold):
        pk = PublicPlainKey()
        sks = [SecretPlainKey(i, threshold) for i in range(n_parties)]
        return pk, sks


class PublicPlainKey():

    def encrypt_get_rand(self, value):
        cipher = PlainCiphertext(self, value)
        r = 0
        return cipher, r

    def encrypt(self, value, use_randomness=True):
        if not isinstance(value, (int, mpz().__class__)):
            raise ValueError('{} is not a valid number (it is of type {}).'.format(value, type(value)))
        c, _ = self.encrypt_get_rand(value)
        return c

    def get_max_plaintext_value(self):
        """returns the maximum value that can be encrypted by this public key"""
        return 2 ** 32

    def get_random_plaintext(self):
        """returns a possible plaintext"""
        return randint(0, self.get_max_plaintext_value())

    def get_r(self):
        return 0


class SecretPlainKey():

    def __init__(self, idx, threshold):
        self.index = idx
        self.threshold = threshold

    def decrypt(self, cipher):
        return cipher


class PlainCiphertext(Ciphertext):

    pass
