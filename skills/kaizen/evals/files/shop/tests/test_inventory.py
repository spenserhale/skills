import unittest

from shop.inventory import reserve


class ReserveTest(unittest.TestCase):
    def test_reserve_reduces_stock(self):
        self.assertEqual(reserve(10, 3), 7)

    def test_reserve_more_than_stock_raises(self):
        with self.assertRaises(ValueError):
            reserve(2, 5)
