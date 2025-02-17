from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    def __hash__(self):
        return hash(tuple(self.model_dump(exclude_unset=True).values()))

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        from_attributes=True,  # `from_orm` equivalent
    )

    def set_without_validation(self, name: str, value: Any) -> None:
        """
        Workaround to be able to set fields without validation.

        Because due to the validate_assignment=True, we can't set fields without validation.
        And as fact, it raises the RecursionError.
        """
        attr = getattr(self.__class__, name, None)

        if isinstance(attr, property):
            attr.__set__(self, value)
        else:
            self.__dict__[name] = value
            self.__pydantic_fields_set__.add(name)
