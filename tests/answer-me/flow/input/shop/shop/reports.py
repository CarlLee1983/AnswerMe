from shop.pricing import compute_total


def monthly_revenue(orders):
    return sum(compute_total(order["items"], order.get("coupon")) for order in orders)
