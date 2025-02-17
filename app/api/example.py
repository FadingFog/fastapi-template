from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.enums import ApiTagEnum
from app.domain.example.schemas import ExampleCreate, ExampleDetail
from app.domain.example.services import ExampleService

example_router = APIRouter(prefix="/example", tags=[ApiTagEnum.EXAMPLE])


@example_router.post("", response_model=ExampleDetail)
async def create_example(
    example_data: ExampleCreate,
    service: Annotated[ExampleService, Depends()],
):
    return await service.create(obj=example_data)
