from pydantic import BaseModel, ConfigDict


class FolderQuery(BaseModel):
    """Folder operations accept no query parameters, including ownership input."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
