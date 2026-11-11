from shop import events
from shop.errors import PaymentDeclined
from shop.pricing import compute_total
from shop.validation import validate_items


class OrderService:
    def __init__(self, orders, inventory, payments):
        self.orders = orders
        self.inventory = inventory
        self.payments = payments

    def place_order(self, customer_id, items, coupon=None):
        validate_items(items)
        total = compute_total(items, coupon)
        reservation = self.inventory.reserve(items)
        try:
            self.payments.charge(customer_id, total)
        except PaymentDeclined:
            self.inventory.release(reservation)
            raise
        order = self.orders.save({"customer_id": customer_id, "items": items, "coupon": coupon, "total": total})
        events.publish("order_placed", order)
        return order
