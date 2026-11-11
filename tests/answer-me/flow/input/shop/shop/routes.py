from shop.errors import OutOfStock, PaymentDeclined, ValidationError
from shop.wiring import build_order_service


def post_order(request, service=None):
    service = service or build_order_service()
    try:
        order = service.place_order(request["customer_id"], request["items"], request.get("coupon"))
    except ValidationError as exc:
        return 400, {"error": str(exc)}
    except OutOfStock as exc:
        return 409, {"error": "out of stock", "sku": str(exc)}
    except PaymentDeclined:
        return 402, {"error": "payment declined"}
    return 201, {"order_id": order["id"], "total": order["total"]}


def get_order(order_id, service=None):
    service = service or build_order_service()
    order = service.orders.find(order_id)
    if order is None:
        return 404, {"error": "not found"}
    return 200, order
