import unittest

from shop.errors import PaymentDeclined
from shop.inventory.repo import InventoryRepo
from shop.orders.repo import OrderRepo
from shop.orders.service import OrderService


class FakePayments:
    def __init__(self, approve=True):
        self.approve = approve
        self.charges = []

    def charge(self, customer_id, amount):
        self.charges.append(amount)
        if not self.approve:
            raise PaymentDeclined("declined")
        return "ch_1"


class OrderServiceTest(unittest.TestCase):
    def test_place_order_charges_total(self):
        payments = FakePayments()
        service = OrderService(OrderRepo(), InventoryRepo({"BOOK": 3}), payments)
        order = service.place_order("c1", [{"sku": "BOOK", "qty": 2}])
        self.assertEqual(order["total"], 735)
        self.assertEqual(payments.charges, [735])

    def test_declined_payment_releases_stock(self):
        inventory = InventoryRepo({"BOOK": 3})
        service = OrderService(OrderRepo(), inventory, FakePayments(approve=False))
        with self.assertRaises(PaymentDeclined):
            service.place_order("c1", [{"sku": "BOOK", "qty": 2}])
        self.assertEqual(inventory.stock["BOOK"], 3)
