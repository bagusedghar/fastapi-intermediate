"""Application: error saat data yang diminta use case tidak ada."""


class NotFound(Exception):
    code = "not_found"


class OrderNotFound(NotFound):
    code = "order_not_found"


class ProductNotFound(NotFound):
    code = "product_not_found"
