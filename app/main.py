from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.api import init_routers
from app.config import config
from app.core.exceptions import exception_handlers
from app.core.middlewares import init_middlewares


def _initialize_app() -> FastAPI:
    _app = FastAPI(
        title=config.title,
        exception_handlers=exception_handlers,
        debug=config.debug,
        docs_url=config.docs_url,
    )

    init_routers(_app)
    init_middlewares(_app)
    add_pagination(_app)

    return _app


app: FastAPI = _initialize_app()
