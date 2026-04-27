"""Tests for the HTML converter."""

from __future__ import annotations

from pathlib import Path

from alchemark import alchemize
from alchemark.core import Alchemist


def test_html_basic_heading(tmp_path: Path) -> None:
    p = tmp_path / "doc.html"
    p.write_text("<h1>Hello World</h1><p>Some text.</p>")

    md = alchemize(p)
    assert "# Hello World" in md
    assert "Some text." in md


def test_html_extracts_metadata(tmp_path: Path) -> None:
    p = tmp_path / "doc.html"
    p.write_text(
        "<html><head><title>My Page</title>"
        '<meta name="author" content="Alice"></head>'
        "<body><p>Hi</p></body></html>"
    )

    a = Alchemist()
    result = a.transmute(p)
    assert result.metadata.get("title") == "My Page"
    assert result.metadata.get("author") == "Alice"


def test_html_strips_scripts(tmp_path: Path) -> None:
    p = tmp_path / "doc.html"
    p.write_text(
        "<html><body>"
        "<script>alert('xss')</script>"
        "<style>body { color: red; }</style>"
        "<p>Real content</p>"
        "</body></html>"
    )

    md = alchemize(p)
    assert "Real content" in md
    assert "alert" not in md
    assert "color: red" not in md


def test_html_lists(tmp_path: Path) -> None:
    p = tmp_path / "doc.html"
    p.write_text("<ul><li>One</li><li>Two</li><li>Three</li></ul>")

    md = alchemize(p)
    assert "- One" in md
    assert "- Two" in md
