"""SRP (Single Responsibility) - BEFORE

OrderManager mengerjakan semuanya: hitung total, simpan data, kirim email.
Kalau format email berubah, class ini diedit. Kalau database ganti, class ini diedit juga.
Padahal SRP: "A class should have only one reason to change."
"""


class OrderManager:
    def __init__(self):
        self.orders: dict[int, dict] = {}

    def place_order(self, customer: str, items: list[dict]) -> dict:
        # 1. hitung total
        subtotal = sum(i["price"] * i["qty"] for i in items)
        total = subtotal - subtotal * 5 // 100

        # 2. simpan
        order = {"id": len(self.orders) + 1, "customer": customer, "total": total}
        self.orders[order["id"]] = order

        # 3. kirim email
        print(f"[EMAIL] ke {customer}: Order #{order['id']} total Rp{total:,}")
        return order


if __name__ == "__main__":
    print(OrderManager().place_order("budi@mail.com", [{"price": 100_000, "qty": 2}]))
