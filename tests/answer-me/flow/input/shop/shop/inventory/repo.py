from shop.errors import OutOfStock


class InventoryRepo:
    def __init__(self, stock):
        self.stock = dict(stock)

    def reserve(self, items):
        for item in items:
            if self.stock.get(item["sku"], 0) < item["qty"]:
                raise OutOfStock(item["sku"])
        for item in items:
            self.stock[item["sku"]] -= item["qty"]
        return list(items)

    def release(self, reservation):
        for item in reservation:
            self.stock[item["sku"]] += item["qty"]
