import math

from unittest import TestCase


class MySampleTest(TestCase):
    def test_math_in_a_loop(self):
        for n in xrange(2 ** 8):
            math.sqrt(n)
