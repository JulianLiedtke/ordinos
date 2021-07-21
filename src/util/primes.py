import logging
import yaml
from os.path import exists, join
from os import getcwd
from threading import Lock
from random import choice, randrange
from gmpy2 import mpz, powmod, invert, is_prime, random_state, mpz_urandomb, log2, mpz_random, gcd, add, mul, fac


log = logging.getLogger(__name__)


class PrimeStorage():
    def __init__(self):
        self.dataPath = join('data', 'primes')
        self.rand = random_state(randrange(1234567891011121314))

    def getRandomSafePrime(self, bitlength):
        """ used to obtain a random prime with given bits. 
        If no such prime is stored, it will generate them"""
        filename = self.getFileName(bitlength)

        if not exists(filename):
            log.info('No primes stored of length {}. Searching for primes...'.format(bitlength))
            self.generateSafePrimes(bitlength)

        file = open(filename, 'r', encoding='utf-8')
        primes = yaml.load(file.read(), Loader=yaml.FullLoader)
        file.close()
        return choice(primes)

    def getRandomSafePrimes(self, bitlength):
        """ used to obtain random safe primes with given bits. 
        If no such primes are stored, it will generate them"""
        filename = self.getFileName(bitlength)

        if not exists(filename):
            log.info('No primes stored of length {}. Searching for primes...'.format(bitlength))
            self.generateSafePrimes(bitlength)

        primes = self.getPrimes(filename)
        #(p, p_) = choice(primes)
        #(q, q_) = choice(primes)
        (p, p_) = primes[0]
        (q, q_) = primes[1]
        # ensure that p != q
        while (p == q):
            (q, q_) = choice(primes)
        return ((p, p_), (q, q_))

    def generateSafePrimes(self, bits, n=2):
        """Generates safe primes of given size and safes them in file for later usage.
        It will search for n new primes"""
        filename = self.getFileName(bits)
        found = 0
        found_primes = []
        if exists(filename):
            found_primes = self.getPrimes(filename)
        while found < n:
            prime = self.generate_safe_prime(bits)
            if prime not in found_primes:
                found_primes.append(prime)
                f = open(filename, 'w', encoding='utf-8')
                primes_str = [(str(p), str(q)) for (p, q) in found_primes]
                f.write(str(yaml.dump(primes_str)))
                f.close()
                found += 1
                log.info('Found {}. prime'.format(len(found_primes)))

    def getPrimes(self, filename):
        """ returns a list of all primes in given file"""
        if exists(filename):
            file = open(filename, 'r', encoding='utf-8')
            primes_str = yaml.load(file.read(), Loader=yaml.FullLoader)
            file.close()
            primes = [(mpz(p), mpz(q)) for (p, q) in primes_str]
            return primes
        else:
            return []

    def getFileName(self, bits):
        return join(getcwd(), self.dataPath, 'primes-{}.yaml'.format(bits))

    def generate_safe_prime(self, bits):
        """Generates a secure prime of input length using the gmpy2 library.
        A secure prime is a prime p of the form p = 2 * q + 1 where q is also a prime.
        The output of this function is (p, q) with p and q as described above.

        The function draws a candidate and tests it. If it is not able to find a good
        candidate, it will run forever.
        """
        while True:
            # generate p, a prime of input length
            p = mpz(2)**(bits-1) + mpz_urandomb(self.rand, (bits-1))
            if is_prime(p):
                # p is prime, get q and test if q is also prime
                q = (p - 1) // 2
                if is_prime(q):
                    return (p, q)