"""Factory: create_notifier() membuat notifier sesuai channel di config."""
from typing import Protocol


class Notifier(Protocol):
    def send(self, to: str, message: str) -> None: ...


class EmailNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[EMAIL] ke {to}: {message}")


class SmsNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[SMS] ke {to}: {message}")


NOTIFIERS = {"email": EmailNotifier, "sms": SmsNotifier}


def create_notifier(channel: str) -> Notifier:
    if channel not in NOTIFIERS:
        raise ValueError(f"Channel tidak dikenal: {channel}")
    return NOTIFIERS[channel]()
