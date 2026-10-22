"""API: exception handler global.

Semua error dikirim ke client dengan format yang sama:
    {"error": {"code": "...", "message": "...", "details": [...] | null}}
Pemetaan error -> HTTP status code ada di sini, karena status code adalah urusan HTTP.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.application.errors import NotFound
from app.domain.errors import DomainError, OrderCannotBeChanged, OutOfStock, UnknownCustomerType

class RateLimited(Exception):
    def __init__(self, limit: int, retry_after: int):
        super().__init__(f"Terlalu banyak request, coba lagi dalam {retry_after} detik")
        self.limit = limit
        self.retry_after = retry_after


STATUS_CODES = {
    UnknownCustomerType: 400,
    OrderCannotBeChanged: 409,
    OutOfStock: 409,
}


def error_response(status_code: int, code: str, message: str, details: list | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code,
                        content={"error": {"code": code, "message": message, "details": details}})


async def handle_not_found(request: Request, exc: NotFound) -> JSONResponse:
    return error_response(404, exc.code, str(exc))


async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    return error_response(STATUS_CODES.get(type(exc), 400), exc.code, str(exc))


async def handle_rate_limited(request: Request, exc: RateLimited) -> JSONResponse:
    response = error_response(429, "rate_limited", str(exc))
    response.headers["Retry-After"] = str(exc.retry_after)
    response.headers["X-RateLimit-Limit"] = str(exc.limit)
    response.headers["X-RateLimit-Remaining"] = "0"
    return response


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [{"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return error_response(422, "validation_error", "Data request tidak valid", details)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFound, handle_not_found)
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(RateLimited, handle_rate_limited)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
