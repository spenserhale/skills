import unittest

from shop.pricing import apply_discount


class ApplyDiscountTest(unittest.TestCase):
    def test_no_code(self):
        self.assertEqual(apply_discount(20), 20.0)

    def test_welcome5(self):
        self.assertEqual(apply_discount(20, "WELCOME5"), 15.0)

    def test_half(self):
        self.assertEqual(apply_discount(19.99, "HALF"), 10.0)

    def test_never_negative(self):
        self.assertEqual(apply_discount(3, "WELCOME5"), 0.0)
