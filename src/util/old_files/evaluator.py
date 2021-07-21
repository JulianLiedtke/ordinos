class Evaluator:
    def set_num_candidates(self, num_candidates):
        self.num_candidates = num_candidates

    def get_num_candidates(self):
        return self.num_candidates

    def set_votes(self, votes):
        self.votes = votes

    def set_add_func(self, add_func):
        self.add_func = add_func

    def add(self, x, y):
        return self.add_func(x, y)

    def set_mult_func(self, mult_func):
        self.mult_func = mult_func

    def mult(self, x, y):
        return self.mult_func(x, y)

    def set_enc_mult_func(self, mult_func):
        self.enc_mult_func = mult_func

    def enc_mult(self, x, y):
        return self.enc_mult_func(x, y)

    def set_sub_func(self, sub_func):
        self.sub_func = sub_func

    def sub(self, x, y):
        return self.sub_func(x, y)

    def get_votes(self):
        return self.votes

    def set_eq(self, eq):
        self.eq_func = eq

    def eq(self, x, y):
        return self.eq_func(x, y)

    def set_gt(self, gt):
        self.gt_func = gt

    def gt(self, x, y):
        return self.gt_func(x, y)

    def set_decryption(self, decrypt):
        self.decrypt_func = decrypt

    def decrypt(self, y):
        return self.decrypt_func(y)

    def set_unified_encryption(self, enc):
        self.unified_encryption = enc

    def encrypt_unified(self, x):
        return self.unified_encryption(x)