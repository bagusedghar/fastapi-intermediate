"""Factory - AFTER

Urusan "class mana yang dibuat" dipindah ke satu function: create_notifier().
Function lain cukup minta notifier, tidak perlu tahu class aslinya.
Tambah channel baru = tambah class + satu baris di NOTIFIERS.
"""


class EmailNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[EMAIL] ke {to}: {message}")


class SmsNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[SMS] ke {to}: {message}")


class WhatsAppNotifier:  # channel baru, place_order & cancel_order tidak disentuh
    def send(self, to: str, message: str) -> None:
        print(f"[WA] ke {to}: {message}")


NOTIFIERS = {
    "email": EmailNotifier,
    "sms": SmsNotifier,
    "whatsapp": WhatsAppNotifier,
}


def create_notifier(channel: str):
    """Factory: terima nama channel, kembalikan object notifier."""
    if channel not in NOTIFIERS:
        raise ValueError(f"Channel tidak dikenal: {channel}")
    return NOTIFIERS[channel]()


def place_order(order_id: int, customer: str, channel: str) -> None:
    create_notifier(channel).send(customer, f"Order #{order_id} berhasil dibuat")


def cancel_order(order_id: int, customer: str, channel: str) -> None:
    create_notifier(channel).send(customer, f"Order #{order_id} dibatalkan")


if __name__ == "__main__":
    place_order(1, "budi@mail.com", "email")
    cancel_order(1, "budi@mail.com", "sms")
    place_order(2, "0812xxxx", "whatsapp")
