import itertools


class OrderRepo:
    def __init__(self):
        self.rows = {}
        self._ids = itertools.count(1)

    def save(self, order):
        order = dict(order, id=next(self._ids))
        self.rows[order["id"]] = order
        return order

    def find(self, order_id):
        return self.rows.get(order_id)
