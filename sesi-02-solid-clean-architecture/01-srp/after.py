"""SRP (Single Responsibility) - AFTER

Setiap class cuma punya satu tugas:
- PriceCalculator : hitung total
- OrderRepository : simpan data
- EmailNotifier   : kirim email
OrderService hanya mengatur urutannya.
"""


class PriceCalculator:
    def total(self, items: list[dict]) -> int:
        subtotal = sum(i["price"] * i["qty"] for i in items)
        return subtotal - subtotal * 5 // 100


class OrderRepository:
    def __init__(self):
        self.orders: dict[int, dict] = {}

    def add(self, customer: str, total: int) -> dict:
        order = {"id": len(self.orders) + 1, "customer": customer, "total": total}
        self.orders[order["id"]] = order
        return order


class EmailNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[EMAIL] ke {to}: {message}")


class OrderService:
    def __init__(self):
        self.calculator = PriceCalculator()
        self.repo = OrderRepository()
        self.notifier = EmailNotifier()

    def place_order(self, customer: str, items: list[dict]) -> dict:
        total = self.calculator.total(items)
        order = self.repo.add(customer, total)
        self.notifier.send(customer, f"Order #{order['id']} total Rp{total:,}")
        return order


if __name__ == "__main__":
    print(OrderService().place_order("budi@mail.com", [{"price": 100_000, "qty": 2}]))
