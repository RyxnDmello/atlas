from uuid import UUID
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FileSource:
    """Capture canonical source identity and name at authorization time."""

    file_id: UUID
    file_name: str


@dataclass(frozen=True, slots=True)
class AuthorizedFileScope:
    """Carry detached, immutable sources resolved by server authorization."""

    files: tuple[FileSource, ...]

    @property
    def file_ids(self) -> frozenset[UUID]:
        """Expose permitted identities without a mutable membership collection."""
        return frozenset(source.file_id for source in self.files)
