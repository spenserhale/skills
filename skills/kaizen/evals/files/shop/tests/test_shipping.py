import unittest

from shop.shipping import shipping_cost


class ShippingCostTest(unittest.TestCase):
    def test_free_at_threshold(self):
        self.assertEqual(shipping_cost(75, 2), 0.0)

    def test_flat_rate_plus_weight(self):
        self.assertEqual(shipping_cost(20, 2), 7.49)
