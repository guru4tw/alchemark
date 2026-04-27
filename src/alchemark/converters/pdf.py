"""PDF → Markdown converter (requires `alchemark[pdf]`)."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

# Trigger ImportError at module load if pdfplumber is missing,
# so the core registry can skip this converter cleanly.
import pdfplumber

from alchemark.converters.base import BaseConverter
from alchemark.core import Result
from alchemark.exceptions import ConversionError


class PdfConverter(BaseConverter):
    """Converts PDF documents to Markdown.

    Note: PDF is a notoriously hard format. This converter handles
    text-based PDFs well; scanned PDFs require the `ocr` extra.
    """

    extensions: ClassVar[list[str]] = [".pdf"]
    name: ClassVar[str] = "pdf"

    def convert(self, path: Path) -> Result:
        warnings: list[str] = []
        all_text: list[str] = []
        metadata: dict[str, str | int] = {}

        try:
            with pdfplumber.open(str(path)) as pdf:
                meta = pdf.metadata or {}
                if meta.get("Title"):
                    metadata["title"] = str(meta["Title"])
                if meta.get("Author"):
                    metadata["author"] = str(meta["Author"])
                metadata["page_count"] = len(pdf.pages)

                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    if not text.strip():
                        warnings.append(
                            f"Page {i} has no extractable text. "
                            f"It may be a scanned image — try `alchemark[ocr]`."
                        )
                        continue
                    all_text.append(text)
        except Exception as e:
            raise ConversionError(
                path,
                f"PDF parsing failed: {e}",
                hint="The PDF may be corrupted, encrypted, or use unsupported features.",
            ) from e

        markdown = "\n\n".join(all_text).strip() + "\n"

        return Result(
            markdown=markdown,
            source=path,
            metadata=metadata,
            warnings=warnings,
        )
