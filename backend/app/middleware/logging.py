from starlette.middleware.base import BaseHTTPMiddleware
from structlog import get_logger

logger = get_logger()


class AccessLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        logger.info("request_completed", method=request.method, path=request.url.path, status=response.status_code)
        return response
