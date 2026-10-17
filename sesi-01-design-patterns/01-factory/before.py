"""Factory - BEFORE

Setiap function yang butuh notifier menentukan sendiri class mana yang dibuat.
If/elif yang sama muncul di dua tempat. Kalau nanti ada channel baru (misal WhatsApp),
semua if/elif ini harus diubah satu per satu.
"""


class EmailNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[EMAIL] ke {to}: {message}")


class SmsNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[SMS] ke {to}: {message}")


def place_order(order_id: int, customer: str, channel: str) -> None:
    if channel == "email":
        notifier = EmailNotifier()
    elif channel == "sms":
        notifier = SmsNotifier()
    else:
        raise ValueError(f"Channel tidak dikenal: {channel}")
    notifier.send(customer, f"Order #{order_id} berhasil dibuat")


def cancel_order(order_id: int, customer: str, channel: str) -> None:
    # if/elif yang sama, hasil copy-paste dari place_order
    if channel == "email":
        notifier = EmailNotifier()
    elif channel == "sms":
        notifier = SmsNotifier()
    else:
        raise ValueError(f"Channel tidak dikenal: {channel}")
    notifier.send(customer, f"Order #{order_id} dibatalkan")


if __name__ == "__main__":
    place_order(1, "budi@mail.com", "email")
    cancel_order(1, "budi@mail.com", "sms")
