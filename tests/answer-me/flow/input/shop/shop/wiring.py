from shop import events, notifications
from shop.inventory.repo import InventoryRepo
from shop.orders.repo import OrderRepo
from shop.orders.service import OrderService
from shop.payments.gateway import PaymentGateway


def build_order_service():
    events.subscribe("order_placed", notifications.send_receipt)
    return OrderService(
        orders=OrderRepo(),
        inventory=InventoryRepo(stock={"BOOK": 3, "PEN": 10}),
        payments=PaymentGateway(base_url="https://pay.example.test"),
    )
