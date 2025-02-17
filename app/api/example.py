from fastapi import APIRouter

from app.core.enums import ApiTagEnum

example_router = APIRouter(prefix="/example", tags=[ApiTagEnum.EXAMPLE])
