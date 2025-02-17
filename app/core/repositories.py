from abc import ABC
from typing import Any, Generic, Sequence
from uuid import UUID

from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Select, delete, inspect, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from sqlalchemy.sql.roles import ColumnsClauseRole

from app.core.exceptions.base_exception import NotFoundError, raise_db_error
from app.core.types import CreateSchema, DetailSchema, Model, UpdateSchema


class CRUDRepository(ABC, Generic[Model, DetailSchema, CreateSchema, UpdateSchema]):
    """
    Base repository class for CRUD operations.
    """

    sql_model: Model

    def __init__(self, session: AsyncSession):
        self.session = session

    def get_query(self) -> Select:
        """
        Returns a query object for the model.

        :return: Query object.
        """
        return select(self.sql_model)

    async def get(
        self,
        obj_id: int | UUID,
        *,
        raise_error: bool = True,
        **kwargs: Any,
    ) -> Model | None:
        """
        This method retrieves an object from the database using its ID.

        :param obj_id: The ID of the object to be retrieved.
        :param raise_error: A flag that determines whether an error should be raised if the object is not found.
                            If True, a NotFoundError will be raised when the object is not found.
                            If False, the method will return None when the object is not found. Default is True.
        :param kwargs: Additional keyword arguments.

        :return: The retrieved object if it exists. If the object does not exist and raise_error is False, the method
                 will return None.

        :raises NotFoundError: If raise_error is True and the object is not found in the database.
        """
        stmt = self.get_query().filter_by(id=obj_id)

        if not (result := await self.session.scalar(stmt)) and raise_error:
            raise NotFoundError(detail=f"{self.sql_model.__name__} object with {obj_id=!s} not found")

        return result

    async def get_all(
        self,
        query_filter: Filter = None,
        raw_result: bool = False,
        *,
        is_unique: bool = False,
        **kwargs: Any,
    ) -> Page[DetailSchema] | list[Model]:  # type: ignore
        """
        This method retrieves all objects from the database.

        :param query_filter: A SQLAlchemy Filter object to filter the objects to be retrieved. Default is None.
        :param raw_result: A flag that determines whether to return a list of raw results without pagination.
                           If True, a list of raw results will be returned.
                           If False, a Page object with paginated results will be returned. Default is False.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.
        :param kwargs: Additional keyword arguments.

        :return: A Page object with paginated results if raw_result is False, otherwise a list of raw results.

        :raises NoResultFound: If no objects are found in the database.
        """
        stmt = self.get_query()

        if query_filter:
            stmt = query_filter.filter(stmt)
            stmt = query_filter.sort(stmt)

        if raw_result:
            if is_unique:
                return (await self.session.execute(stmt)).unique().all()  # type: ignore

            return (await self.session.scalars(stmt)).all()  # type: ignore

        return await paginate(self.session, stmt)

    async def get_by_ids(self, obj_ids: Sequence[int | UUID]) -> list[Model]:
        """
        Returns a list of objects by their IDs.

        :param obj_ids: List of IDs.

        :return: List of objects.
        """
        # noinspection PyTypeChecker
        stmt = self.get_query().where(self.sql_model.id.in_(obj_ids)).options(noload("*"))  # type: ignore[attr-defined]

        return (await self.session.scalars(stmt)).all()  # type: ignore

    async def _apply_changes(
        self,
        stmt,
        obj_id: int | UUID = None,
        *,
        is_unique: bool,
        autocommit: bool,
    ) -> Model:
        """
        Internal method to store changes in DB.
        """
        try:
            result = await self.session.execute(stmt)

            if is_unique:
                result = result.unique()

            result = result.scalar_one()

            if autocommit:
                await self.session.commit()
            else:
                await self.session.flush()

            await self.session.refresh(result)

        except DBAPIError as exc:
            await self.session.rollback()
            raise_db_error(exc)

        except NoResultFound:
            raise NotFoundError(detail=f"{self.sql_model.__name__} object with {obj_id=!s} not found")

        return result

    async def create(
        self,
        obj_data: dict,
        *,
        autocommit: bool = True,
        is_unique: bool = True,
        **kwargs: Any,
    ) -> Model:
        """
        Creates an entity in the database and returns the created object.

        :param obj_data: The object to create.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.
        :param kwargs: Additional keyword arguments.

        :return: The created object.
        """
        stmt = insert(self.sql_model).values(**obj_data).returning(self.sql_model)

        return await self._apply_changes(stmt=stmt, autocommit=autocommit, is_unique=is_unique)

    async def update(
        self,
        obj_id: int | UUID,
        obj_data: dict,
        *,
        autocommit: bool = True,
        is_unique: bool = True,
        **kwargs: Any,
    ) -> Model:
        """
        Updates an object.

        :param obj_data: The object data to update.
        :param obj_id: The ID of the object to update.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.

        :returns: The updated object.
        """
        stmt = update(self.sql_model).filter_by(id=obj_id).values(**obj_data).returning(self.sql_model)

        return await self._apply_changes(stmt=stmt, obj_id=obj_id, autocommit=autocommit, is_unique=is_unique)

    async def delete(
        self,
        obj_id: int | UUID,
        *,
        autocommit: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Delete an object.

        :param obj_id: The ID of the object to delete.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.

        :raises DBAPIError: If there is an error during database operations.
        :raises NotFoundError: If item does not exist in a database.
        """
        await self.get(obj_id=obj_id)

        stmt = delete(self.sql_model).filter_by(id=obj_id)

        try:
            await self.session.execute(stmt)

            if autocommit:
                await self.session.commit()
            else:
                await self.session.flush()

        except DBAPIError as exc:
            await self.session.rollback()
            raise_db_error(exc)

    def get_select_entities(self, exclude_columns: list[str] | None = None) -> list[ColumnsClauseRole]:
        """
        Returns a list of SQLAlchemy column entities to be used in a SELECT statement.

        The method inspects the model's columns and constructs a list of SQLAlchemy column entities.
        It excludes the specified columns if provided.

        :param exclude_columns: Columns to be excluded from the result.

        :return: A list of SQLAlchemy column entities.
        """
        exclude_columns = set(exclude_columns or [])

        mapper = inspect(self.sql_model)

        return [
            getattr(self.sql_model, entity.key)
            for entity in mapper.c  # type: ignore[attr-defined]
            if entity.key not in exclude_columns  # type: ignore
        ]

    def expire(self, instance: Model, attribute_names: list[str]) -> None:
        return self.session.expire(instance=instance, attribute_names=attribute_names)
