import json
import logging
import math
import time
import unittest

from src.crypto.plain_abb import PlainABB
from src.election.trustee import init_trustees
from src.protocols.protocol import (DecProtocol, EqDecProtocol, GtDecProtocol,
                                    MulDecProtocol, Protocol)
from src.protocols.protocol_suite import EmptyProtocolSuite
from src.util.logging import setup_logging
from src.util.protocol_runner import ProtocolRunner

log = logging.getLogger(__name__)


class PlainABBTest(unittest.TestCase):

    def setUp(self):
        setup_logging()
        self.test_runs = 10
        self.bits_key = 64
        self.n_shares = 5
        self.threshold = 3

        self.trustees = PlainABB.gen_trustees(self.bits_key, self.n_shares, self.threshold, EmptyProtocolSuite)
        self.abb = self.trustees[0].abb

        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        log.info("%s: %.3f" % (self.id(), t))

    def test_correctness_without_randomness(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            enc_x = self.abb.enc_no_r(x)
            eval = ProtocolRunner(self.trustees, DecProtocol)
            result, _ = eval.run([enc_x])
            self.assertEqual(result, x)

    def test_correctness_with_randomness(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            enc_x = self.abb.enc(x)
            eval = ProtocolRunner(self.trustees, DecProtocol)
            result, _ = eval.run([enc_x])
            self.assertEqual(result, x)

    def test_zero(self):
        for _ in range(self.test_runs):
            x = 0
            enc_x = self.abb.enc(x)
            eval = ProtocolRunner(self.trustees, DecProtocol)
            result, _ = eval.run([enc_x])
            self.assertEqual(result, x)

    def test_one(self):
        for _ in range(self.test_runs):
            x = 1
            enc_x = self.abb.enc(x)
            eval = ProtocolRunner(self.trustees, DecProtocol)
            result, _ = eval.run([enc_x])
            self.assertEqual(result, x)

    def test_add_ciphers(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            x_ = self.abb.enc(x)
            y = self.abb.get_random_plaintext()
            y_ = self.abb.enc(y)
            z_ = x_ + y_
            eval = ProtocolRunner(self.trustees, DecProtocol)
            z, _ = eval.run([z_])
            self.assertEqual(z, x + y)

    def test_add_const(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            x_ = self.abb.enc(x)
            y = self.abb.get_random_plaintext()
            z_ = x_ + y
            eval = ProtocolRunner(self.trustees, DecProtocol)
            z, _ = eval.run([z_])
            self.assertEqual(z, x + y)

    def test_r_add_const(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            y = self.abb.get_random_plaintext()
            y_ = self.abb.enc(y)
            z_ = x + y_
            eval = ProtocolRunner(self.trustees, DecProtocol)
            z, _ = eval.run([z_])
            self.assertEqual(z, x + y)

    def test_mult_const(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            x_ = self.abb.enc(x)
            y = self.abb.get_random_plaintext()
            z_ = x_ * y
            eval = ProtocolRunner(self.trustees, DecProtocol)
            z, _ = eval.run([z_])
            self.assertEqual(z, x * y)

    def test_sub_ciphers(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            x_ = self.abb.enc(x)
            y = self.abb.get_random_plaintext()
            y_ = self.abb.enc(y)
            z_ = x_ - y_
            eval = ProtocolRunner(self.trustees, DecProtocol)
            z, _ = eval.run([z_])
            self.assertEqual(z, x - y)

    def test_sub_const(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            x_ = self.abb.enc(x)
            y = self.abb.get_random_plaintext()
            z_ = x_ - y
            eval = ProtocolRunner(self.trustees, DecProtocol)
            z, _ = eval.run([z_])
            self.assertEqual(z, x - y)

    def test_eq_0_0(self):
        self._test_eq(0, 0)

    def test_eq_0_1(self):
        self._test_eq(0, 1)

    def test_eq_1_0(self):
        self._test_eq(1, 0)

    def test_eq_1_1(self):
        self._test_eq(1, 1)

    def test_gt_0_0(self):
        self._test_gt(0, 0)

    def test_gt_0_1(self):
        self._test_gt(0, 1)

    def test_gt_1_0(self):
        self._test_gt(1, 0)

    def test_gt_1_1(self):
        self._test_gt(1, 1)

    def test_mul_0_0(self):
        self._test_mul(0, 0)

    def test_mul_0_1(self):
        self._test_mul(0, 1)

    def test_mul_1_0(self):
        self._test_mul(1, 0)

    def test_mul_1_1(self):
        self._test_mul(1, 1)

    def test_gt(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            y = self.abb.get_random_plaintext()
            self._test_gt(x, y)

    def test_eq(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            y = self.abb.get_random_plaintext()
            self._test_eq(x, y)

    def test_mul(self):
        for _ in range(self.test_runs):
            x = self.abb.get_random_plaintext()
            y = self.abb.get_random_plaintext()
            self._test_mul(x, y)

    def _test_gt(self, x, y):
        x_ = self.abb.enc(x)
        y_ = self.abb.enc(y)
        eval = ProtocolRunner(self.trustees, GtDecProtocol)
        z, _ = eval.run([x_, y_, None])
        self.assertEqual(z, x >= y)

    def _test_eq(self, x, y):
        x_ = self.abb.enc(x)
        y_ = self.abb.enc(y)
        eval = ProtocolRunner(self.trustees, EqDecProtocol)
        z, _ = eval.run([x_, y_, None])
        self.assertEqual(z, x == y)

    def _test_mul(self, x, y):
        x_ = self.abb.enc(x)
        y_ = self.abb.enc(y)
        eval = ProtocolRunner(self.trustees, MulDecProtocol)
        z, _ = eval.run([x_, y_])
        self.assertEqual(z, x * y)
