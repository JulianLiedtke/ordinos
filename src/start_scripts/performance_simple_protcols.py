

import sys
from time import time

from src.crypto.paillier_abb import PaillierABB
from src.election.trustee import init_trustees
from src.protocols.sublinear import (SublinearMultiplicationProtocol,
                                          SublinearEqProtocol, SublinearGtProtocol)
from src.protocols.sublinear import SubLinearProtocolSuite
from src.util.logging import setup_logging
from src.util.protocol_runner import ProtocolRunner
import random
from src.protocols.protocol import DecProtocol


def test_performance_basic_ops(key_generator):
    trustees = key_generator()
    abb = trustees[0].abb.create_local_abb()

    bits_numbers = []
    current_bits = 2
    while (current_bits <= abb.pk.bits / 4):
        bits_numbers.append(current_bits)
        current_bits *= 2

    enc_x=[]
    enc_y=[]
    for i in range(len(bits_numbers)):
        enc_x.append(abb.enc(2**(bits_numbers[i] - 1)))
        enc_y.append(abb.enc(2**(bits_numbers[i] - 1)))

    start_time = time()
    for i in range(len(bits_numbers)):
        ProtocolRunner(trustees, DecProtocol).run([enc_x[i]])
    print('dec-avg')
    print(('%.3f' % ((time() - start_time) / len(bits_numbers))).replace('.',','))

    start_time = time()
    for i in range(len(bits_numbers)):
        ProtocolRunner(trustees, SublinearMultiplicationProtocol).run([enc_x[i], enc_y[i]])
    print('mul-avg')
    print(('%.3f' % ((time() - start_time) / len(bits_numbers))).replace('.',','))

    print("eqs: ")
    for i in range(5):
        if i < len(bits_numbers):
            start_time = time()
            ProtocolRunner(trustees, SublinearEqProtocol).run([enc_x[i] - enc_y[i], bits_numbers[i]])
            print(('%.3f' % (time() - start_time)).replace('.',','))
        else:
            print("")
    print("")
    print("")

    print("gts: ")
    for i in range(5):
        if i < len(bits_numbers):
            start_time = time()
            ProtocolRunner(trustees, SublinearGtProtocol).run([enc_x[i], enc_y[i], bits_numbers[i]])
            print(('%.3f' % (time() - start_time)).replace('.',','))
        else:
            print("")
    print("")
    print("")

def test_performance_specific_basic_ops(key_generator):
    trustees = key_generator()
    abb = trustees[0].abb.create_local_abb()

    check_one_protocol(DecProtocol, 'Decrypt       ', 100, abb, trustees, 1)
    check_one_protocol(SublinearMultiplicationProtocol, 'Multiplication', 100, abb, trustees, 2)
    check_one_protocol(SublinearEqProtocol, 'Eq  4 bit     ', 10, abb, trustees, 2, bits=4)
    check_one_protocol(SublinearEqProtocol, 'Eq  8 bit     ', 10, abb, trustees, 2, bits=8)
    check_one_protocol(SublinearEqProtocol, 'Eq 16 bit     ', 10, abb, trustees, 2, bits=16)
    check_one_protocol(SublinearEqProtocol, 'Eq 32 bit     ', 10, abb, trustees, 2, bits=32)
    check_one_protocol(SublinearGtProtocol, 'Gt  4 bit     ', 10, abb, trustees, 2, bits=4)
    check_one_protocol(SublinearGtProtocol, 'Gt  8 bit     ', 10, abb, trustees, 2, bits=8)
    check_one_protocol(SublinearGtProtocol, 'Gt 16 bit     ', 10, abb, trustees, 2, bits=16)
    check_one_protocol(SublinearGtProtocol, 'Gt 32 bit     ', 10, abb, trustees, 2, bits=32)


def check_one_protocol(protocol, name, accuracy, abb, trustees, value_count, bits = None):
    times = []
    # 4 bit gt
    for _ in range(accuracy):
        values = []
        for __ in range(value_count):
            if bits == None:
                values.append(abb.enc(random.randint(0, 2**8-1)))
            else:
                values.append(abb.enc(random.randint(0, 2**bits-1)))
        if bits != None:
            values.append(bits)
        start_time = time()
        ProtocolRunner(trustees, protocol).run(values)
        times.append(time()-start_time)

    print('%s: Avg: %8.3f, Min:%8.3f, Max: %8.3f' % (name, sum(times)/len(times), min(times), max(times)))


if __name__ == '__main__':
    setup_logging()

    bits_key = int(sys.argv[1]) if len(sys.argv) > 1 else 256
    trustee_count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    specific_test = int(sys.argv[4]) if len(sys.argv) > 3 else 0

    if (specific_test > 0):
        test_performance_specific_basic_ops(lambda: PaillierABB.gen_trustees(bits_key, trustee_count, threshold, SubLinearProtocolSuite))
    else:
        test_performance_basic_ops(lambda: PaillierABB.gen_trustees(bits_key, trustee_count, threshold, SubLinearProtocolSuite))
