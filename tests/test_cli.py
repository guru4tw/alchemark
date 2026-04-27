"""Tests for the Alchemark CLI."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from alchemark import __version__
from alchemark.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_help_shown_when_no_args() -> None:
    # `no_args_is_help=True` means bare invocation prints help and exits 0/2.
    result = runner.invoke(app, [])
    assert "Transmute documents into Markdown gold" in result.stdout
    assert "convert" in result.stdout
    assert "formats" in result.stdout


def test_cli_formats_lists_known_extensions() -> None:
    result = runner.invoke(app, ["formats"])
    assert result.exit_code == 0
    assert ".docx" in result.stdout
    assert ".html" in result.stdout
    assert ".pdf" in result.stdout
    assert ".pptx" in result.stdout


def test_cli_convert_html_to_stdout(tmp_path: Path) -> None:
    src = tmp_path / "doc.html"
    src.write_text("<h1>Hello</h1><p>World.</p>", encoding="utf-8")
    result = runner.invoke(app, ["convert", str(src)])
    assert result.exit_code == 0
    assert "# Hello" in result.stdout
    assert "World." in result.stdout


def test_cli_convert_html_to_file(tmp_path: Path) -> None:
    src = tmp_path / "doc.html"
    src.write_text("<h1>Hello</h1>", encoding="utf-8")
    out = tmp_path / "out.md"
    result = runner.invoke(app, ["convert", str(src), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "# Hello" in out.read_text(encoding="utf-8")
    # Success line goes to stdout
    assert "Wrote" in result.stdout


def test_cli_convert_quiet_suppresses_progress(tmp_path: Path) -> None:
    src = tmp_path / "doc.html"
    src.write_text("<h1>Hi</h1>", encoding="utf-8")
    out = tmp_path / "out.md"
    result = runner.invoke(app, ["convert", str(src), "-o", str(out), "--quiet"])
    assert result.exit_code == 0
    assert out.exists()
    # Quiet suppresses the success/progress line
    assert "Wrote" not in result.stdout


def test_cli_convert_missing_file_shows_did_you_mean(tmp_path: Path) -> None:
    (tmp_path / "report.html").write_text("<p>hi</p>")
    typo = tmp_path / "reprot.html"
    result = runner.invoke(app, ["convert", str(typo)])
    assert result.exit_code == 1
    # Newer typer captures stdout+stderr together in `output`; rich panels print to stderr.
    output = result.output
    assert "Cannot find" in output
    assert "report.html" in output  # the close match


def test_cli_convert_unsupported_format_shows_hint(tmp_path: Path) -> None:
    weird = tmp_path / "thing.xyz"
    weird.write_text("nope", encoding="utf-8")
    result = runner.invoke(app, ["convert", str(weird)])
    assert result.exit_code == 1
    output = result.output
    assert "Unsupported file format" in output
    assert ".xyz" in output
    assert "guru4tw/alchemark/issues" in output
