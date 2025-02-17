from fastapi import Request, WebSocket, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import log
from app.core.exceptions.base_exception import BaseError


async def validation_error_handler(_: Request, exc: ValidationError):
    log.info(f"{exc.__class__.__name__}", error=str(exc))

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": "Validation error",
            "detail": "Provided values are not valid.",
        },
    )


async def base_error_handler(request: Request | WebSocket, exc: BaseError):
    log.error(f"{exc.__class__.__name__}", error=str(exc))

    if isinstance(request, WebSocket):
        raise exc

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.content,
    )
