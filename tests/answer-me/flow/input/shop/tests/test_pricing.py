import unittest

from shop.pricing import compute_total


class PricingTest(unittest.TestCase):
    def test_total_includes_tax(self):
        self.assertEqual(compute_total([{"sku": "PEN", "qty": 4}]), 105)
