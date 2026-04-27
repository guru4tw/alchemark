"""Core conversion logic — the Alchemist's workshop."""

from __future__ import annotations

import difflib
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from alchemark.converters.base import BaseConverter
from alchemark.exceptions import MissingFileError, UnsupportedFormatError


@dataclass
class Result:
    """The outcome of a transmutation.

    Attributes:
        markdown: The converted Markdown text.
        source: Path to the original document.
        metadata: Document metadata (title, author, etc.) if available.
        warnings: Non-fatal issues encountered during conversion.
    """

    markdown: str
    source: Path
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return self.markdown

    def save(self, path: str | Path) -> Path:
        """Save the markdown to a file. Returns the path written to."""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.markdown, encoding="utf-8")
        return out


class Alchemist:
    """The main conversion engine.

    Args:
        preserve_images: If True, extract images and reference them in markdown.
        image_dir: Where to write extracted images (default: alongside output).
        on_warning: Callback for non-fatal warnings during conversion.
    """

    def __init__(
        self,
        *,
        preserve_images: bool = False,
        image_dir: str | Path | None = None,
        on_warning: Callable[[str], None] | None = None,
    ) -> None:
        self.preserve_images = preserve_images
        self.image_dir = Path(image_dir) if image_dir else None
        self.on_warning = on_warning
        self._converters: dict[str, type[BaseConverter]] = {}
        self._register_builtin_converters()

    def _register_builtin_converters(self) -> None:
        """Register all built-in converters. Optional ones are registered lazily."""
        from alchemark.converters.docx import DocxConverter
        from alchemark.converters.html import HtmlConverter

        self.register(DocxConverter)
        self.register(HtmlConverter)

        # Optional converters — register only if dependencies are available.
        try:
            from alchemark.converters.pdf import PdfConverter

            self.register(PdfConverter)
        except ImportError:
            pass

        try:
            from alchemark.converters.pptx import PptxConverter

            self.register(PptxConverter)
        except ImportError:
            pass

        try:
            from alchemark.converters.image import ImageConverter

            self.register(ImageConverter)
        except ImportError:
            pass

    def register(self, converter_cls: type[BaseConverter]) -> None:
        """Register a converter for its supported extensions."""
        for ext in converter_cls.extensions:
            self._converters[ext.lower()] = converter_cls

    @property
    def supported_extensions(self) -> list[str]:
        """Return a sorted list of supported file extensions."""
        return sorted(self._converters.keys())

    def transmute(self, source: str | Path) -> Result:
        """Convert a single document to Markdown."""
        path = Path(source)

        if not path.exists():
            suggestions = self._find_similar_files(path)
            raise MissingFileError(path, suggestions)

        ext = path.suffix.lower()
        converter_cls = self._converters.get(ext)
        if converter_cls is None:
            raise UnsupportedFormatError(path, self.supported_extensions)

        converter = converter_cls(
            preserve_images=self.preserve_images,
            image_dir=self.image_dir,
        )
        result = converter.convert(path)

        if self.on_warning:
            for warning in result.warnings:
                self.on_warning(warning)

        return result

    def transmute_all(self, pattern: str | Path) -> Iterator[Result]:
        """Convert multiple documents matching a glob pattern."""
        pattern_path = Path(pattern)
        if pattern_path.is_dir():
            paths = [
                p
                for p in pattern_path.iterdir()
                if p.is_file() and p.suffix.lower() in self._converters
            ]
        else:
            base = pattern_path.parent if pattern_path.parent != Path("") else Path(".")
            paths = list(base.glob(pattern_path.name))

        for path in paths:
            yield self.transmute(path)

    @staticmethod
    def _find_similar_files(path: Path) -> list[Path]:
        """Suggest similarly-named files in the parent directory."""
        parent = path.parent if path.parent != Path("") else Path(".")
        if not parent.exists():
            return []
        candidates = [p.name for p in parent.iterdir() if p.is_file()]
        matches = difflib.get_close_matches(path.name, candidates, n=3, cutoff=0.6)
        return [parent / m for m in matches]


def alchemize(source: str | Path, **options: Any) -> str:
    """Convert a document to Markdown — the simplest possible API.

    Args:
        source: Path to the document.
        **options: Passed to Alchemist (preserve_images, image_dir, etc.)

    Returns:
        The Markdown content as a string.

    Example:
        >>> import alchemark
        >>> md = alchemark.alchemize("report.docx")
    """
    alchemist = Alchemist(**options)
    result = alchemist.transmute(source)
    return result.markdown
