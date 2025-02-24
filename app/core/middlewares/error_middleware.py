import traceback
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import log
from app.core.constants import SERVER_ERROR_MESSAGE


class ErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions raised during request processing.

    This middleware catches all exceptions, logs the error details including
    the traceback for debugging, and then sends a JSON response indicating an
    internal server error to the client.

    Returns:
        Response: A FastAPI `JSONResponse` if an exception occurs, indicating a
                  500 Internal Server Error with a generic error message. If no
                  exception occurs, returns the response from the actual endpoint
                  handler.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)

        except Exception as exc:
            log.error(
                "An error occurred during request processing",
                error=str(exc),
                stack_trace=traceback.format_exc(),
                url=request.url.path,
                method=request.method,
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "title": "Server error",
                    "detail": SERVER_ERROR_MESSAGE,
                },
            )
