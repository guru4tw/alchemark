"""Alchemark CLI — the alchemist's command line."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from alchemark import __version__
from alchemark.core import Alchemist
from alchemark.exceptions import AlchemarkError

app = typer.Typer(
    name="alchemark",
    help="🧪 Transmute documents into Markdown gold.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"alchemark [cyan]{__version__}[/cyan]")
        raise typer.Exit()


@app.callback()
def _main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """🧪 Alchemark — transmute documents into Markdown gold."""


@app.command()
def convert(
    source: Path = typer.Argument(..., help="Path to the document to convert."),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. Defaults to stdout.",
    ),
    preserve_images: bool = typer.Option(
        False,
        "--preserve-images",
        help="Extract and reference images in the output.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress warnings and progress messages.",
    ),
) -> None:
    """Convert a document to Markdown."""
    alchemist = Alchemist(
        preserve_images=preserve_images,
        on_warning=None if quiet else lambda w: err_console.print(f"[yellow]⚠[/yellow]  {w}"),
    )

    try:
        result = alchemist.transmute(source)
    except AlchemarkError as e:
        _render_error(e)
        raise typer.Exit(code=1) from None

    if output:
        result.save(output)
        if not quiet:
            console.print(
                f"[green]✓[/green] Wrote {len(result.markdown)} chars to [cyan]{output}[/cyan]"
            )
    else:
        sys.stdout.write(result.markdown)


@app.command()
def formats() -> None:
    """List all supported document formats."""
    alchemist = Alchemist()
    table = Table(title="Supported formats", show_header=True, header_style="bold cyan")
    table.add_column("Extension")
    table.add_column("Status")

    # Every supported extension is now bundled by default; image formats simply
    # carry an extra note that the OS-level Tesseract binary is needed for OCR.
    ocr_exts = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"}
    all_known = [
        ".docx",
        ".html",
        ".htm",
        ".pdf",
        ".pptx",
        ".png",
        ".jpg",
        ".jpeg",
        ".tiff",
        ".bmp",
        ".gif",
    ]

    enabled = set(alchemist.supported_extensions)
    for ext in all_known:
        if ext in enabled:
            note = "needs Tesseract binary" if ext in ocr_exts else ""
            if note:
                status = f"[green]✓ built-in[/green] [dim]— {note}[/dim]"
            else:
                status = "[green]✓ built-in[/green]"
        else:
            status = "[dim]✗ not registered[/dim]"
        table.add_row(ext, status)

    console.print(table)


def _render_error(e: AlchemarkError) -> None:
    body = f"[bold red]{e.message}[/bold red]"
    if e.hint:
        body += f"\n\n[yellow]Hint:[/yellow] {e.hint}"
    err_console.print(Panel(body, title="❌ Alchemark Error", border_style="red"))


if __name__ == "__main__":
    app()
