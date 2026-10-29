"""API: exception handler global.

Semua error dikirim ke client dengan format yang sama:
    {"error": {"code": "...", "message": "...", "details": [...] | null, "request_id": "..."}}
Pemetaan error -> HTTP status code ada di sini, karena status code adalah urusan HTTP.

Setiap error juga dicatat di log dengan field error_type:
- client     : kesalahan request (4xx). WARNING, tidak memicu alert
- dependency : database, Redis, atau broker sedang gangguan (503). ERROR, biasanya pulih sendiri
- bug        : error yang tidak terduga (500). ERROR + traceback
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from kombu.exceptions import OperationalError as BrokerError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError
from sqlalchemy.exc import OperationalError as DatabaseError

from app.application.errors import NotFound
from app.domain.errors import DomainError, OrderCannotBeChanged, OutOfStock, UnknownCustomerType
from app.infrastructure.logs import request_id_var

logger = logging.getLogger("app.errors")


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
DEPENDENCY_ERRORS = (DatabaseError, RedisConnectionError, RedisTimeoutError, BrokerError)


def error_response(status_code: int, code: str, message: str, details: list | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {
        "code": code, "message": message, "details": details, "request_id": request_id_var.get()}})


def client_error(request: Request, status_code: int, code: str, message: str,
                 details: list | None = None) -> JSONResponse:
    logger.warning("request ditolak: %s", code, extra={
        "error_type": "client", "error_code": code, "status": status_code, "path": request.url.path})
    return error_response(status_code, code, message, details)


async def handle_not_found(request: Request, exc: NotFound) -> JSONResponse:
    return client_error(request, 404, exc.code, str(exc))


async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    return client_error(request, STATUS_CODES.get(type(exc), 400), exc.code, str(exc))


async def handle_rate_limited(request: Request, exc: RateLimited) -> JSONResponse:
    response = client_error(request, 429, "rate_limited", str(exc))
    response.headers["Retry-After"] = str(exc.retry_after)
    response.headers["X-RateLimit-Limit"] = str(exc.limit)
    response.headers["X-RateLimit-Remaining"] = "0"
    return response


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [{"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return client_error(request, 422, "validation_error", "Data request tidak valid", details)


async def handle_dependency_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("dependency gangguan: %s", type(exc).__name__, extra={
        "error_type": "dependency", "path": request.url.path})
    return error_response(503, "service_unavailable", "Layanan sedang gangguan, coba lagi beberapa saat")


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("error tidak terduga", exc_info=exc, extra={"error_type": "bug", "path": request.url.path})
    return error_response(500, "internal_error", "Terjadi kesalahan di server")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFound, handle_not_found)
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(RateLimited, handle_rate_limited)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    for error in DEPENDENCY_ERRORS:
        app.add_exception_handler(error, handle_dependency_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
