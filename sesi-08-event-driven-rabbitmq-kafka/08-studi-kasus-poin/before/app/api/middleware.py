"""API: middleware yang membungkus semua request."""
import time

from fastapi import Request


async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{ms:.1f}ms"
    print(f"{request.method} {request.url.path} {response.status_code} {ms:.1f}ms")
    return response
