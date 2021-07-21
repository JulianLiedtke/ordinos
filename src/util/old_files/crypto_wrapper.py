
class Cryptodata():

    def __init__(self, protocol, key, num_bits):
        self.protocol = protocol
        self.key = key
        self.num_bits = num_bits

    def encrypt(self, value):
        """ encrypts a plaintext with the generated public key without randomness"""
        return self.key.encrypt(value, use_randomness=False)

    def encrypt_rand(self, value):
        """ encrypts a plaintext with the generated public key with randomness"""
        return self.key.encrypt(value, use_randomness=True)

    def decrypt(self, y):
        """ decrypts a ciphertext"""
        return self.protocol.decrypt(y)

    def add(self, x, y):
        """ adds two ciphertexts """
        return x+y

    def sub(self, x, y):
        """ subtracts ciphertext y from ciphertext x """
        return x-y

    def mult(self, x, y):
        """ multiplies ciphertext by constant """
        return x*y

    def mult_ciphers(self, x, y):
        """ multiplies two ciphertexts """
        return self.protocol.mul(x, y)

    def greater_than_test(self, x, y, bitlength=None):
        """ returns an encrypted 1 iff x >= y """
        return self.protocol.gt(x, y, self.num_bits)

    def equality_test(self, x, y, bitlength=None):
        """ return an encrypted 1 iff x == y """
        return self.protocol.eq(x, y, self.num_bits)