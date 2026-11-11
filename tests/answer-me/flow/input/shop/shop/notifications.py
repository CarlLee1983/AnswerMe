SENT = []


def send_receipt(order):
    SENT.append({"to": order["customer_id"], "order_id": order["id"], "total": order["total"]})
