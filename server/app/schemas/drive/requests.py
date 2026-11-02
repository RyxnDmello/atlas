from uuid import UUID
from typing import Annotated, Self

from pydantic.json_schema import SkipJsonSchema
from pydantic import AfterValidator, BaseModel, ConfigDict, StringConstraints, model_validator


def description(value: str | None) -> str | None:
    """Normalize optional metadata without inventing a database length limit."""
    return value.strip() or None if value is not None else None


Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Description = Annotated[str | None, AfterValidator(description)]


class FolderCreate(BaseModel):
    """Validate metadata and immutable initial location for a new owned folder."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    name: Name
    description: Description = None
    parent_id: UUID | None = None


class FolderPatch(BaseModel):
    """Keep omitted fields distinct from an explicitly cleared description."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    name: Name | SkipJsonSchema[None] = None
    description: Description = None

    @model_validator(mode="after")
    def supplied(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Supply folder metadata")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("Folder name cannot be null")

        return self
