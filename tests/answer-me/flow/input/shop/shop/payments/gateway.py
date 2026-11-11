from shop.errors import PaymentDeclined


class PaymentGateway:
    def __init__(self, base_url, http=None):
        self.base_url = base_url
        self.http = http

    def charge(self, customer_id, amount):
        response = self.http.post(f"{self.base_url}/charges", json={"customer": customer_id, "amount": amount})
        if response["status"] != "approved":
            raise PaymentDeclined(response["status"])
        return response["charge_id"]
