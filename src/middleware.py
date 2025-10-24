import time
import uuid

from logger import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from structlog.contextvars import bind_contextvars, clear_contextvars


class StructlogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        clear_contextvars()
        bind_contextvars(
            request_id=request_id,
            http_method=request.method,
            http_path=request.url.path,
            endpoint=self._resolve_endpoint_name(request),
        )

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            bind_contextvars(duration_ms=duration_ms)
            await logger.aexception("request failed")
            clear_contextvars()
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        bind_contextvars(status_code=response.status_code, duration_ms=duration_ms)
        response.headers["x-request-id"] = request_id
        await logger.adebug("request completed")
        clear_contextvars()
        return response

    @staticmethod
    def _resolve_endpoint_name(request: Request) -> str | None:
        endpoint = request.scope.get("endpoint")
        return getattr(endpoint, "__name__", None)
