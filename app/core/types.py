from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

from app.core.models import Base

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from app.core.repositories import CRUDRepository

Repository = TypeVar("Repository", bound="CRUDRepository")
DetailSchema = TypeVar("DetailSchema", bound=BaseModel)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel, contravariant=True)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel, contravariant=True)
Model = TypeVar("Model", bound=Base)
