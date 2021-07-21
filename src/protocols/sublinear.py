import abc
import logging
from os import getcwd, makedirs
from os.path import exists, join
from random import choice, randrange
from threading import Lock

import numpy as np
import yaml

from gmpy2 import (add, f_div, fac, gcd, invert, mpz, mpz_random, mul, powmod,
                   random_state, log2)
from src.protocols.protocol import Protocol
from src.protocols.protocol_suite import ProtocolSuite
from src.util.utils import get_binary_representation, if_then_else, minus1to

log = logging.getLogger(__name__)


class SubLinearProtocolSuite(ProtocolSuite):

    def __init__(self):
        super().__init__()

    def add(self, cipher1, cipher2):
        raise NotImplementedError()

    def mul(self, cipher1, cipher2):
        protocol = self.init_protocol(SublinearMultiplicationProtocol())
        return protocol.start(cipher1, cipher2)

    def eq(self, cipher1, cipher2, bits):
        protocol = self.init_protocol(SublinearEqProtocol())
        return protocol.start(cipher1, cipher2, bits)

    def gt(self, cipher1, cipher2, bits):
        protocol = self.init_protocol(SublinearGtProtocol())
        return protocol.start(cipher1, cipher2, bits)


class SublinearMultiplicationProtocol(Protocol):

    def run(self, enc_x, enc_y):
        enc_d, enc_e = self.run_subprotocol(
            BroadcastRandomMultProtocol(), [enc_y])

        enc_s = enc_x
        for enc_d_i in enc_d:
            enc_s += enc_d_i[1]

        s = self.abb.dec(enc_s)

        enc_mult = enc_y * s
        enc_res = enc_mult
        for enc_e_i in enc_e:
            enc_res = enc_res - enc_e_i[1]

        return enc_res


class SublinearEqProtocol(Protocol):

    def run(self, cipher1, cipher2, bits_int):
        storage = EqStorage(self.abb)
        data = storage.get_data(bits_int)

        enc_x = cipher1 - cipher2

        enc_m = enc_x + data['enc_r']
        m = self.abb.dec(enc_m)
        enc_shifted_h_dist = self.calc_enc_h_dist(m, bits_int, data)
        enc_m_h = data['enc_R_inv'] * enc_shifted_h_dist
        m_h = self.abb.dec(enc_m_h)
        enc_powers = [data['enc_pow_R'][i-1] * powmod(
            m_h, i, self.abb.pk.n) for i in range(1, bits_int + 2)]
        enc_eval = self.abb.enc_no_r(data['poly_coeffs'][0])

        max_power = min(len(data['poly_coeffs']), len(enc_powers))
        for i in range(1, len(data['poly_coeffs'])):
            temp = enc_powers[i-1] * data['poly_coeffs'][i]
            enc_eval = enc_eval + temp

        return enc_eval

    def calc_enc_h_dist(self, m, bits_int, data):
        bin_m = get_binary_representation(m, bits_int)
        enc_h_dist = self.abb.enc_no_r(0)
        for i in range(bits_int):
            bit_m = bin_m[len(bin_m) - i - 1]
            enc_bit_r = data['enc_bits_r'][len(data['enc_bits_r']) - i - 1]
            enc_s = enc_bit_r + bit_m
            enc_neg_p = enc_bit_r * (- 2 * bit_m)
            enc_xor = enc_s + enc_neg_p
            enc_h_dist = enc_h_dist + enc_xor
        # Add 1 to hamming distance
        return enc_h_dist + 1


class SublinearGtProtocol(Protocol):

    def run(self, enc_x, enc_y, bits_int):
        storage = GtStorage(self.abb)
        data = storage.get_data(bits_int)

        if bits_int == 1:
            return self.recursion_abort(enc_x, enc_y)

        # enc z
        enc_diff = self.get_enc_diff(enc_x, enc_y)
        enc_z = enc_diff + (2**bits_int)

        # calc m
        powmod_half = powmod(2, int(bits_int/2), self.abb.pk.n)
        enc_m = enc_z + data['enc_r']
        m = self.abb.dec(enc_m)
        m_low = m % powmod_half
        m_high = f_div(m, powmod_half) % powmod_half
        enc_m_high = self.abb.enc_no_r(m_high)

        # eq test
        enc_b = self.abb.eq(enc_m_high, data['enc_r_top'], bits_int//2)

        # calc tilde
        enc_m_tilde = if_then_else(enc_b, m_low, m_high)
        enc_r_diff = self.get_enc_diff(data['enc_r_bot'], data['enc_r_top'])
        enc_r_tilde = (enc_b * enc_r_diff) + data['enc_r_top']

        # rec step
        enc_gt_tilde = self.abb.gt(enc_m_tilde, enc_r_tilde, bits_int // 2)

        # calc result
        enc_f = enc_gt_tilde * (-1) + 1
        powmod_all = powmod(2, bits_int, self.abb.pk.n)
        enc_f_mul = enc_f * powmod_all
        enc_r_sum = data['enc_r_top'] * powmod_half + data['enc_r_bot']
        enc_help_diff = self.get_enc_diff(enc_f_mul, enc_r_sum)
        enc_z_mod = enc_help_diff + (m % powmod_all)

        enc_z_diff = self.get_enc_diff(enc_z, enc_z_mod)

        return enc_z_diff * invert(powmod_all, self.abb.pk.n)

    def recursion_abort(self, enc_x, enc_y):
        enc_product = enc_x * enc_y
        enc_neg_y = enc_y * (-1)
        return enc_neg_y + 1 + enc_product

    def get_enc_diff(self, enc_x, enc_y):
        return self.run_subprotocol(EncDiffProtocol(), [enc_x, enc_y])


class BroadcastRandomMultProtocol(Protocol):

    def run(self, enc_y):
        d = self.abb.get_random_plaintext()
        enc_d, r = self.abb.enc_get_r(d)
        enc_e = enc_y * d

        proof = self.run_subprotocol(ProofCorrectMulProtocol(), [enc_y, enc_d, enc_e, d, r, 1])

        enc_d_list = self.broadcast_and_receive(enc_d)
        enc_e_list = self.broadcast_and_receive(enc_e)
        zk_proofs = self.broadcast_and_receive(proof)

        for enc_d, enc_e, proof in zip(enc_d_list, enc_e_list, zk_proofs):
            v = self.run_subprotocol(VerifyCorrectMulProtocol(), [enc_y, enc_d[1], enc_e[1], proof[1][0], proof[1][1], proof[1][2]])
            if not v:
                raise ValueError('ZK proof failed.')

        return enc_d_list, enc_e_list


class EncDiffProtocol(Protocol):

    def run(self, enc_x, enc_y):
        return enc_x + (enc_y * (-1))


class ProofCorrectMulProtocol(Protocol):

    def run(self, enc_x, enc_y, enc_z, y, r, s):
        # announcement
        a = self.abb.get_random_plaintext()
        enc_a, u = self.abb.enc_get_r(a)
        enc_b = enc_x * a
        v = self.abb.get_r()
        enc_b = self.abb.randomize(enc_b, r=v)
        announcement = (enc_a, enc_b)

        # challenge
        c = self.abb.get_r()

        # response
        d = a + c * y
        e = u * powmod(r, c, self.abb.pk.n)
        f = v * powmod(s, c, self.abb.pk.n)
        response = (d, e, f)

        return (announcement, c, response)


class VerifyCorrectMulProtocol(Protocol):

    def run(self, enc_x, enc_y, enc_z, ann, c, res):
        enc_a, enc_b = ann
        d, e, f = res

        left = self.abb.enc_no_r(d)
        left = self.abb.randomize(left, r=e)

        right = (enc_y * c) + enc_a

        if not left.val == right.val:
            log.info('First check of VerifyCorrectMulProtocol fails.')
            return False

        left = enc_x * d
        left = self.abb.randomize(left, r=f)

        right = (enc_z * c) + enc_b

        if not left.val == right.val:
            log.info('Second check of VerifyCorrectMulProtocol fails.')
            return False

        return True


class SublinearStorage():

    __metaclass__ = abc.ABCMeta
    lock = Lock()

    def __init__(self, prot, abb):
        self.abb = abb
        self.rand = random_state(randrange(1234567891011121314))
        abb_name = type(self.abb).__name__
        self.data_path = join('data', 'sublinear', abb_name, prot)
        self.create_dir(self.data_path)

    def create_dir(self, dir):
        makedirs(dir, exist_ok=True)

    def get_data(self, bits_int):
        """ used to obtain data with given bits. 
        If no such data is stored, it will be generated """
        self.lock.acquire()
        result = None
        try:
            generate = False
            filename = self._get_filename(self.abb.pk.bits, bits_int)
            if not exists(filename):
                generate = True
            else:
                data = self._load_data_file(filename)
                if not str(self.abb.pk.n) in data.keys():
                    generate = True
            if generate:
                log.info('No data stored for this parameters.')
                self._generate_data(filename, bits_int)

            data = self._load_data_file(filename)
            result = self._recreate_data(data[str(self.abb.pk.n)])
        finally:
            self.lock.release()
        return result

    def _get_filename(self, key_bits, int_bits):
        return join(getcwd(), self.data_path, '{}K-{}-I.yaml'.format(key_bits, int_bits))

    def _load_data_file(self, filename):
        file = open(filename, 'r', encoding='utf-8')
        out = yaml.load(file.read(), Loader=yaml.FullLoader)
        file.close()
        return out

    @abc.abstractclassmethod
    def _generate_data(self, filename, int_bits):
        pass

    @abc.abstractclassmethod
    def _recreate_data(self, data_str):
        pass


class EqStorage(SublinearStorage):

    def __init__(self, abb):
        super().__init__('eq', abb)

    def _generate_data(self, filename, int_bits):
        rand_r, rand_bits_r, rand_R_exp, rand_R_inv = self._gen_unenc_randomness(
            int_bits, self.abb.pk.n)
        enc_bits_r = [self.abb.enc(rand_bit) for rand_bit in rand_bits_r]
        enc_r = self.abb.enc(rand_r)
        enc_R_inv = self.abb.enc(rand_R_inv)
        enc_pow_R = [self.abb.enc(rand_R_power) for rand_R_power in rand_R_exp]
        poly_coeffs = self._generate_poly_coeffs(int_bits, self.abb.pk.n)[int_bits - 1]

        data = {}
        data['enc_bits_r'] = [str(r) for r in enc_bits_r]
        data['enc_r'] = str(enc_r)
        data['enc_R_inv'] = str(enc_R_inv)
        data['enc_pow_R'] = [str(r) for r in enc_pow_R]
        data['poly_coeffs'] = [str(c) for c in poly_coeffs]

        content = {}
        if exists(filename):
            content = self._load_data_file(filename)
        content[str(self.abb.pk.n)] = data

        f = open(filename, 'w', encoding='utf-8')
        f.write(str(yaml.dump(content)))
        f.close()

    def _recreate_data(self, data_str):
        data = {}
        data['enc_bits_r'] = [self.abb.init_cipher(mpz(r)) for r in data_str['enc_bits_r']]
        data['enc_r'] = self.abb.init_cipher(mpz(data_str['enc_r']))
        data['enc_R_inv'] = self.abb.init_cipher(mpz(data_str['enc_R_inv']))
        data['enc_pow_R'] = [self.abb.init_cipher(mpz(r)) for r in data_str['enc_pow_R']]
        data['poly_coeffs'] = [mpz(r) for r in data_str['poly_coeffs']]
        return data

    def _gen_unenc_randomness(self, int_bits, modulus, k=0):
        """ creates unencrypted randomness needed for an equality test """
        if k == 0:
            l = int(log2(modulus))
            k = powmod(2, l - int_bits - 1, modulus)

        random_r = mpz_random(self.rand, k)
        random_bits = get_binary_representation(random_r, int_bits)

        random_R = mpz_random(self.rand, modulus)
        while gcd(random_R, modulus) != 1:
            random_R = mpz_random(self.rand, modulus)
        random_R_exp = [powmod(random_R, i, modulus)
                        for i in range(1, int_bits+2)]

        random_R_inv = invert(random_R, modulus)

        return random_r, random_bits, random_R_exp, random_R_inv

    def _generate_poly_coeffs(self, degree, modulus):
        degree = degree + 1

        # instantiate matrix
        coefficients = [[mpz(0) for x in range(degree+1)]
                        for y in range(degree)]
        for k in range(degree):
            coefficients[k][k+1] = mpz(1)

        # recursive construction (table)
        for k in range(degree):
            coefficients[k][1] = mul(minus1to(k), fac(k+1))
            for l in range(1, k):
                coefficients[k][l+1] = mul(minus1to(k+l), (add(
                    abs(coefficients[k-1][l]), abs(mul(coefficients[k-1][l+1], (k+1))))))

        # scaling
        for k in range(degree):
            for l in range(degree+1):
                coefficients[k][l] = mul(coefficients[k][l], mul(
                    minus1to(k), invert(fac(k), modulus))) % modulus

        return coefficients[1:]


class GtStorage(SublinearStorage):

    def __init__(self, abb):
        super().__init__('gt', abb)

    def _generate_data(self, filename, bits_int):
        max_val = int(pow(2, bits_int / 2))

        r_top = mpz_random(self.rand, max_val)
        r_bot = mpz_random(self.rand, max_val)

        kappa = self.abb.pk.bits - 1 - bits_int
        r_parties = mpz_random(self.rand, int(pow(2, kappa) - 1)) + 1

        r = int(pow(2, bits_int)) * r_parties + \
            int(pow(2, bits_int / 2)) * r_top + r_bot

        enc_r = self.abb.enc(r)
        enc_r_bot = self.abb.enc(r_bot)
        enc_r_top = self.abb.enc(r_top)

        data = {}
        data['enc_r'] = str(enc_r)
        data['enc_r_bot'] = str(enc_r_bot)
        data['enc_r_top'] = str(enc_r_top)

        content = {}
        if exists(filename):
            content = self._load_data_file(filename)
        content[str(self.abb.pk.n)] = data

        f = open(filename, 'w', encoding='utf-8')
        f.write(str(yaml.dump(content)))
        f.close()

    def _recreate_data(self, data_str):
        data = {}
        data['enc_r'] = self.abb.init_cipher(mpz(data_str['enc_r']))
        data['enc_r_bot'] = self.abb.init_cipher(mpz(data_str['enc_r_bot']))
        data['enc_r_top'] = self.abb.init_cipher(mpz(data_str['enc_r_top']))
        return data
