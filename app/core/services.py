from abc import ABC
from typing import Annotated, Any, Callable, Generic, Sequence, Type
from uuid import UUID

from fastapi import Depends
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.core.exceptions.base_exception import BadRequestError
from app.core.types import CreateSchema, Model, Repository, UpdateSchema


class CRUDService(ABC, Generic[Repository, Model, CreateSchema, UpdateSchema]):
    """
    CRUD service for SQLAlchemy models.
    """

    repository_class: Type[Repository]
    filter_depend: Callable = FilterDepends
    filter_class: Type[Filter] = Filter

    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
        self.repository: Repository = self.repository_class(db_session)

    async def get(self, obj_id: int | UUID, *, raise_error: bool = True, **kwargs: Any) -> Model:
        """
        Get an object by id.

        :param obj_id: Object ID.
        :param raise_error: If True, raises an error if the object is not found.
        :param kwargs: Additional keyword arguments.

        :return: Model instance.
        """
        return await self.repository.get(obj_id, raise_error=raise_error, **kwargs)

    async def get_all(self, query_filter: Filter = None, **kwargs: Any) -> Page[Model]:
        """
        Get all objects.

        :param query_filter: Filter object.
        :param kwargs: Additional keyword arguments.

        :return: Paginated result.
        """
        return await self.repository.get_all(query_filter, **kwargs)

    async def get_by_ids(self, obj_ids: Sequence[int | UUID]) -> list[Model]:
        """
        Get objects by IDs.

        :param obj_ids: Object IDs.

        :return: List of model instances.
        """
        return await self.repository.get_by_ids(obj_ids)

    async def create(
        self, obj: CreateSchema, *, obj_id: int | UUID = None, autocommit: bool = True, **kwargs: Any
    ) -> Model:
        """
        Creates an entity in the database, and returns the created object.

        :param obj: Pydantic model.
        :param obj_id: Object ID.
        :param autocommit: If True, commits changes to a database, if False - flushes them.
        :param kwargs: Additional keyword arguments.

        :return: Created model instance.
        """
        obj_data: dict[str, Any] = obj.model_dump() | {"id": obj_id} if obj_id else obj.model_dump()

        return await self.repository.create(obj_data, autocommit=autocommit, **kwargs)

    async def update(self, obj_id: int | UUID, obj: UpdateSchema, *, autocommit: bool = True, **kwargs: Any) -> Model:
        """
        Updates an entity in the database, and returns the updated object.

        :param obj_id: Object ID.
        :param obj: Object to update.
        :param autocommit: If True, commits changes to a database, if False - flushes them.
        :param kwargs: Additional keyword arguments.

        :return: Updated model instance.
        """
        if not (obj_data := obj.model_dump(exclude_defaults=True)):
            raise BadRequestError("No data provided for updating")

        return await self.repository.update(obj_id, obj_data, autocommit=autocommit, **kwargs)

    async def delete(self, obj_id: int | UUID, *, autocommit: bool = True, **kwargs: Any) -> None:
        """
        Deletes an entity from the database.

        :param obj_id: Object ID.
        :param autocommit: If True, commits changes to a database, if False - flushes them.
        :param kwargs: Additional keyword arguments.

        :return: None.
        """
        await self.repository.delete(obj_id, autocommit=autocommit)

    async def upsert(
        self, obj_id: int | UUID | None, obj: CreateSchema, *, autocommit: bool = True, **kwargs: Any
    ) -> Model:
        """
        Updates or creates an entity in the database, and returns the updated or created object.

        :param obj_id: Object ID.
        :param obj: Object to update or create.
        :param autocommit: If True, commits changes to a database, if False-flushes them.
        :param kwargs: Additional keyword arguments.

        :return: Updated or created model instance.
        """
        if obj_id and await self.get(obj_id, raise_error=False):
            return await self.update(obj_id, obj, autocommit=autocommit, **kwargs)

        return await self.create(obj, obj_id=obj_id, autocommit=autocommit, **kwargs)
