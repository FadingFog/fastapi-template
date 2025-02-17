from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse

root_router = APIRouter()


def init_routers(app: FastAPI):
    app.include_router(root_router, default_response_class=ORJSONResponse, prefix="/api")
