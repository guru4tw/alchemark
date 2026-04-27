"""Base class for all document converters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from alchemark.core import Result


class BaseConverter(ABC):
    """Abstract base class for document converters.

    Subclasses must:
      1. Set the `extensions` class variable (e.g. [".docx"])
      2. Implement `convert(path) -> Result`

    Subclasses may:
      - Override `__init__` to accept additional options
      - Use `self.preserve_images` and `self.image_dir`
    """

    extensions: ClassVar[list[str]] = []
    name: ClassVar[str] = ""

    def __init__(
        self,
        *,
        preserve_images: bool = False,
        image_dir: Path | None = None,
    ) -> None:
        self.preserve_images = preserve_images
        self.image_dir = image_dir

    @abstractmethod
    def convert(self, path: Path) -> Result:
        """Convert the document at `path` to a Result."""
        raise NotImplementedError
