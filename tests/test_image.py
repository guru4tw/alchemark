"""Tests for the Image (OCR) converter."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from alchemark.core import Alchemist
from alchemark.exceptions import ConversionError

pytest.importorskip("pytesseract")
pytest.importorskip("PIL")


def _tesseract_available() -> bool:
    """Check whether the Tesseract binary itself is on PATH."""
    if shutil.which("tesseract"):
        return True
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


tesseract_required = pytest.mark.skipif(
    not _tesseract_available(),
    reason="tesseract binary not installed on this system",
)


@pytest.fixture
def text_image(tmp_path: Path) -> Path:
    """Create a PNG with simple, OCR-friendly text."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (600, 120), color="white")
    draw = ImageDraw.Draw(img)
    # Try to use a larger built-in font for better OCR accuracy.
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            size=36,
        )
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 30), "OCR TEST", fill="black", font=font)

    out = tmp_path / "text.png"
    img.save(out)
    return out


@pytest.fixture
def blank_image(tmp_path: Path) -> Path:
    from PIL import Image

    img = Image.new("RGB", (200, 80), color="white")
    out = tmp_path / "blank.png"
    img.save(out)
    return out


def test_image_converter_registered_when_extra_installed() -> None:
    a = Alchemist()
    assert ".png" in a.supported_extensions
    assert ".jpg" in a.supported_extensions


@tesseract_required
def test_image_extracts_text(text_image: Path) -> None:
    a = Alchemist()
    result = a.transmute(text_image)
    # Tesseract on a clean image should produce *some* text.
    # We check for at least one word-like token from the source phrase.
    assert any(token in result.markdown.upper() for token in ("OCR", "TEST"))


@tesseract_required
def test_image_metadata_records_dimensions(text_image: Path) -> None:
    a = Alchemist()
    result = a.transmute(text_image)
    assert result.metadata["width"] == 600
    assert result.metadata["height"] == 120
    assert result.metadata["format"] == "PNG"


@tesseract_required
def test_image_blank_emits_warning(blank_image: Path) -> None:
    a = Alchemist()
    result = a.transmute(blank_image)
    assert any("ocr" in w.lower() or "blank" in w.lower() for w in result.warnings)


def test_image_corrupted_raises_conversion_error(tmp_path: Path) -> None:
    bad = tmp_path / "broken.png"
    bad.write_bytes(b"not really a PNG")
    a = Alchemist()
    with pytest.raises(ConversionError) as exc_info:
        a.transmute(bad)
    assert "broken.png" in str(exc_info.value)
