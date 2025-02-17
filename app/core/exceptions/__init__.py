__all__ = [
    "BaseError",
    "exception_handlers",
]

from pydantic import ValidationError

from .base_exception import BaseError
from .error_handlers import base_error_handler, validation_error_handler

exception_handlers = {
    BaseError: base_error_handler,
    ValidationError: validation_error_handler,
}
