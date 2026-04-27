"""Image (OCR) → Markdown converter (requires `alchemark[ocr]`).

Uses Tesseract under the hood. You must have the Tesseract binary
installed on your system in addition to the Python package:

  macOS:   brew install tesseract
  Ubuntu:  apt-get install tesseract-ocr
  Windows: https://github.com/UB-Mannheim/tesseract/wiki
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pytesseract  # noqa: F401  # ensures registry skips on missing dep

from alchemark.converters.base import BaseConverter
from alchemark.core import Result
from alchemark.exceptions import ConversionError


class ImageConverter(BaseConverter):
    """Extracts text from images using OCR and returns Markdown."""

    extensions: ClassVar[list[str]] = [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]
    name: ClassVar[str] = "image"

    def convert(self, path: Path) -> Result:
        from PIL import Image
        from pytesseract import TesseractNotFoundError, image_to_string

        try:
            img = Image.open(path)
        except Exception as e:
            raise ConversionError(
                path,
                f"Could not open image: {e}",
                hint="The file may be corrupted or in an unsupported format.",
            ) from e

        try:
            text = image_to_string(img)
        except TesseractNotFoundError as e:
            raise ConversionError(
                path,
                "Tesseract binary not found on this system.",
                hint=(
                    "Install Tesseract:\n"
                    "      macOS:   brew install tesseract\n"
                    "      Ubuntu:  sudo apt-get install tesseract-ocr\n"
                    "      Windows: https://github.com/UB-Mannheim/tesseract/wiki"
                ),
            ) from e
        except Exception as e:
            raise ConversionError(
                path,
                f"OCR failed: {e}",
            ) from e

        warnings: list[str] = []
        if not text.strip():
            warnings.append(
                "OCR produced no text. The image may be blank, "
                "low-resolution, or contain non-Latin scripts (try setting lang)."
            )

        metadata = {
            "width": img.width,
            "height": img.height,
            "format": img.format or "",
        }

        markdown = text.strip() + "\n" if text.strip() else ""

        return Result(
            markdown=markdown,
            source=path,
            metadata=metadata,
            warnings=warnings,
        )
