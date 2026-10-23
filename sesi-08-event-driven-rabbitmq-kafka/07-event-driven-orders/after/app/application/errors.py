"""Application: error dari use case."""


class NotFound(Exception):
    code = "not_found"


class OrderNotFound(NotFound):
    code = "order_not_found"


class ProductNotFound(NotFound):
    code = "product_not_found"


class InvalidEvent(Exception):
    """Isi event tidak sesuai format. Dicoba ulang pun tetap gagal."""
