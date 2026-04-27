"""Tests for the PDF converter."""

from __future__ import annotations

from pathlib import Path

import pytest

from alchemark import alchemize
from alchemark.core import Alchemist

# Skip the entire module if optional [pdf] extra isn't installed.
pytest.importorskip("pdfplumber")


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a small text-based PDF using reportlab."""
    reportlab = pytest.importorskip("reportlab")  # noqa: F841
    from reportlab.pdfgen import canvas

    out = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(out))
    c.setTitle("Sample Title")
    c.setAuthor("Sample Author")
    c.drawString(100, 750, "Hello PDF World")
    c.drawString(100, 730, "This is line two.")
    c.showPage()
    c.drawString(100, 750, "Second page content.")
    c.save()
    return out


@pytest.fixture
def empty_pdf(tmp_path: Path) -> Path:
    """Create a PDF with no extractable text (simulates a scanned page)."""
    pytest.importorskip("reportlab")
    from reportlab.pdfgen import canvas

    out = tmp_path / "blank.pdf"
    c = canvas.Canvas(str(out))
    # Draw nothing — single empty page.
    c.showPage()
    c.save()
    return out


def test_pdf_extracts_text(sample_pdf: Path) -> None:
    md = alchemize(sample_pdf)
    assert "Hello PDF World" in md
    assert "This is line two." in md
    assert "Second page content." in md


def test_pdf_metadata(sample_pdf: Path) -> None:
    a = Alchemist()
    result = a.transmute(sample_pdf)
    assert result.metadata["title"] == "Sample Title"
    assert result.metadata["author"] == "Sample Author"
    assert result.metadata["page_count"] == 2


def test_pdf_empty_page_emits_warning(empty_pdf: Path) -> None:
    a = Alchemist()
    result = a.transmute(empty_pdf)
    # Should have at least one warning suggesting OCR
    assert any("ocr" in w.lower() for w in result.warnings)


def test_pdf_warnings_propagate_to_callback(sample_pdf: Path, empty_pdf: Path) -> None:
    seen: list[str] = []
    a = Alchemist(on_warning=seen.append)
    a.transmute(empty_pdf)
    assert seen, "expected at least one warning forwarded to on_warning callback"
