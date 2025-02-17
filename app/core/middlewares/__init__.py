from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config

from .error_middleware import ErrorMiddleware


def init_middlewares(app: FastAPI) -> FastAPI:
    """
    Wrap FastAPI application, with various of middlewares

    **NOTE** Middlewares are executed in the reverse order of their addition. Similar to LIFO stack, not FIFO queue.
    For example, All middlewares must depend on the CORSMiddleware, that's why new middlewares must be added before.
    Middleware for measuring request's execution time should be added after CORS middleware.

    To ensure that all unprocessed errors are caught and that other middleware logic is applied correctly,
    the ErrorMiddleware should be added last.
    """
    app.add_middleware(ErrorMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.origins,
        allow_credentials=config.cors.allow_credentials,
        allow_methods=config.cors.methods,
        allow_headers=config.cors.headers,
    )

    return app
