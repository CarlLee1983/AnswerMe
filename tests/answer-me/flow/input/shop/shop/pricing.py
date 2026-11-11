PRICES = {"BOOK": 350, "PEN": 25}
COUPONS = {"WELCOME10": 0.10}
TAX_RATE = 0.05


def compute_total(items, coupon=None):
    subtotal = sum(PRICES[item["sku"]] * item["qty"] for item in items)
    taxed = subtotal * (1 + TAX_RATE)
    discount = COUPONS.get(coupon, 0)
    return round(taxed * (1 - discount))
