from shop.errors import ValidationError
from shop.pricing import PRICES


def validate_items(items):
    if not items:
        raise ValidationError("empty order")
    for item in items:
        if item["sku"] not in PRICES:
            raise ValidationError(f"unknown sku {item['sku']}")
        if item["qty"] <= 0:
            raise ValidationError("qty must be positive")
