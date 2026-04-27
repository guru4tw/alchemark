"""HTML → Markdown converter."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from alchemark.converters.base import BaseConverter
from alchemark.core import Result
from alchemark.exceptions import ConversionError


class HtmlConverter(BaseConverter):
    """Converts HTML documents to Markdown."""

    extensions: ClassVar[list[str]] = [".html", ".htm"]
    name: ClassVar[str] = "html"

    def convert(self, path: Path) -> Result:
        try:
            from bs4 import BeautifulSoup
            from markdownify import markdownify
        except ImportError as e:  # pragma: no cover
            raise ConversionError(
                path,
                "Required packages are not installed",
                hint="Install them with: pip install markdownify beautifulsoup4",
            ) from e

        try:
            html = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                html = path.read_text(encoding="latin-1")
            except Exception as e:
                raise ConversionError(
                    path,
                    f"Could not read file: {e}",
                    hint="The file may use an unsupported encoding.",
                ) from e

        soup = BeautifulSoup(html, "html.parser")

        # Extract metadata
        metadata: dict[str, str | int] = {}
        if soup.title and soup.title.string:
            metadata["title"] = soup.title.string.strip()

        for meta in soup.find_all("meta"):
            raw_name = meta.get("name", "")
            raw_content = meta.get("content", "")
            # bs4 may return str | list[str] | None — narrow to str.
            if not isinstance(raw_name, str) or not isinstance(raw_content, str):
                continue
            name = raw_name.lower()
            if name in ("author", "description", "keywords") and raw_content:
                metadata[name] = raw_content

        # Strip script/style noise before conversion
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # Convert
        markdown = markdownify(
            str(soup),
            heading_style="ATX",
            bullets="-",
            code_language="",
        )

        # Clean up: collapse excessive blank lines
        lines = [line.rstrip() for line in markdown.splitlines()]
        cleaned: list[str] = []
        blank_count = 0
        for line in lines:
            if not line:
                blank_count += 1
                if blank_count <= 2:
                    cleaned.append(line)
            else:
                blank_count = 0
                cleaned.append(line)

        markdown = "\n".join(cleaned).strip() + "\n"

        return Result(
            markdown=markdown,
            source=path,
            metadata=metadata,
            warnings=[],
        )
