from gmpy2 import mpz, is_even


def init_empty_cand_dict(n_cand, enc_zero):
    """each candidate initialized with 0 points"""
    cand_dict = {}
    for cand in range(n_cand):
        cand_dict[cand] = enc_zero

    return cand_dict


def if_then_else(cond, val_true, val_false):
    """
    A simple if then else branching.
    Inputs/Output:
    - cond (0 or 1, can be encrypted)
    - val_true (return if cond=1)
    - val_false (return if cond=0)
    """
    return cond * val_true + (1 - cond) * val_false


def ext_euclid(n, m):
    a_ = n
    b_ = m
    x_0 = 1
    y_0 = 0
    x_1 = 0
    y_1 = 1

    while b_ != 0:
        q = a_ // b_
        r = a_ % b_
        a_ = b_
        b_ = r
        x_0_ = x_0
        y_0_ = y_0
        x_0 = x_1
        y_0 = y_1
        x_1 = x_0_ - q * x_1
        y_1 = y_0_ - q * y_1

    result = m * y_0
    while result < 0:
        result += n*m
    return result


def eval_polynomial(coeffs, x, n):
    """
    this functions evals the polynomial 
    p(x) = coeffs[n-1]x^(n-1) + ... + 
    coeffs[1]x^1 + coeffs[0] mod n
    """
    y = 0
    for i, coeff in enumerate(coeffs):
        y += coeff * x ** i
        y %= n
    return y


def get_binary_representation(m, bits):
    """ Return the binary representation of m of length bits
    This function adds leading zeros if necessary and will 
    cut leading bits if m > 2**bits """
    bin_m = bin(m)[2:].zfill(bits)
    return [int(i) for i in bin_m]


def minus1to(k):
    if is_even(k):
        return 1
    return -1


def calc_lambda(shares, own_index, delta):
    """calculates lambda used for interpolation"""
    y = mpz(delta)
    for share in shares:
        if share[0] != own_index:
            y *= -share[0]
            y /= (own_index - share[0])
    return mpz(y)
