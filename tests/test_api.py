"""Tests for the public Alchemark API."""

from __future__ import annotations

from pathlib import Path

import pytest

import alchemark
from alchemark import Alchemist, UnsupportedFormatError
from alchemark.exceptions import MissingFileError


def test_alchemize_function_exists() -> None:
    assert callable(alchemark.alchemize)


def test_alchemist_lists_supported_extensions() -> None:
    a = Alchemist()
    exts = a.supported_extensions
    assert ".docx" in exts
    assert ".html" in exts


def test_unsupported_format_raises(tmp_path: Path) -> None:
    weird = tmp_path / "something.xyz"
    weird.write_text("hello")

    a = Alchemist()
    with pytest.raises(UnsupportedFormatError) as exc_info:
        a.transmute(weird)
    assert exc_info.value.hint is not None
    assert ".xyz" in str(exc_info.value)


def test_missing_file_suggests_alternatives(tmp_path: Path) -> None:
    (tmp_path / "report.html").write_text("<p>hi</p>")
    typo = tmp_path / "reprot.html"

    a = Alchemist()
    with pytest.raises(MissingFileError) as exc_info:
        a.transmute(typo)
    # The hint should mention the close match
    assert "report.html" in (exc_info.value.hint or "")


def test_result_str_returns_markdown(tmp_path: Path) -> None:
    html_path = tmp_path / "test.html"
    html_path.write_text("<h1>Hello</h1>")
    a = Alchemist()
    result = a.transmute(html_path)
    assert str(result) == result.markdown


def test_result_save_writes_file(tmp_path: Path) -> None:
    html_path = tmp_path / "test.html"
    html_path.write_text("<h1>Hello</h1>")
    a = Alchemist()
    result = a.transmute(html_path)

    out = tmp_path / "out" / "test.md"
    result.save(out)
    assert out.exists()
    assert "Hello" in out.read_text(encoding="utf-8")
