import logging

log = logging.getLogger(__name__)


class ABBLogger():

    def __init__(self):
        self.count_gt_operations = {}
        self.count_eq_operations = {}
        self.count_dec_operations = 0
        self.count_mul_operations = 0

        self.is_logging_active = True

    def log_dec(self, n=1):
        if self.is_logging_active:
            self.count_dec_operations += n

    def log_eq(self, bits, n=1):
        if self.is_logging_active:
            self._add_ops_bits(self.count_eq_operations, bits, n=n)

    def log_gt(self, bits, n=1):
        if self.is_logging_active:
            self._add_ops_bits(self.count_gt_operations, bits, n=n)

    def log_mul(self, n=1):
        if self.is_logging_active:
            self.count_mul_operations += n

    def op_done(self):
        self.is_logging_active = True

    def start_op(self):
        self.is_logging_active = False

    def _add_ops_bits(self, op_dict, bits, n=1):
        if bits in op_dict:
            op_dict[bits] += n
        else:
            op_dict[bits] = n

    def get_count_gt_operations(self):
        """dict: bits -> count"""
        return self.count_gt_operations

    def get_count_eq_operations(self):
        """dict: bits -> count"""
        return self.count_eq_operations

    def get_count_dec_operations(self):
        """as int"""
        return self.count_dec_operations

    def get_count_mul_operations(self):
        """as int"""
        return self.count_mul_operations
