from unicodedata import category
from typing import Annotated, Self

from pydantic.json_schema import SkipJsonSchema
from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator


def name(value: str) -> str:
    """Normalize upload and PATCH names against the same approved alphabet."""
    value = value.strip()
    if not 1 <= len(value) <= 100 or any(
        category(char)[0] not in {"L", "N"} and char not in " _-.,()[]&+@'"
        for char in value
    ):
        raise ValueError("Invalid file name")

    return value


def description(value: str | None) -> str | None:
    """Normalize optional file metadata without imposing a character whitelist."""
    value = value.strip() or None if value is not None else None
    if value is not None and len(value) > 250:
        raise ValueError("Invalid file description")

    return value


Name = Annotated[str, AfterValidator(name)]
Description = Annotated[str | None, AfterValidator(description)]


class FilePatch(BaseModel):
    """Distinguish omitted metadata from an explicitly cleared description."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    name: Name | SkipJsonSchema[None] = None
    description: Description = None

    @model_validator(mode="after")
    def supplied(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Supply file metadata")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("File name cannot be null")

        return self
