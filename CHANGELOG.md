# Changelog

All notable changes to Alchemark will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **All converters are now bundled by default** — `pip install alchemark`
  installs DOCX/HTML/PDF/PPTX/OCR support in one step. No more
  `pip install alchemark[pdf]` / `[pptx]` / `[ocr]` / `[all]`.
  Old extra names (`pdf`, `pptx`, `ocr`, `all`) are kept as empty no-op
  aliases so existing scripts keep working without changes.
  Image OCR still requires the external Tesseract binary on PATH —
  see README for install instructions.

### Added
- **PPTX image extraction & embedding**. When `preserve_images=True`, every
  picture (including those inside grouped shapes) is extracted to disk and
  referenced under its slide. Image-only slides — previously a single empty
  `## Slide N` — now show the picture(s).
- **Clickable image hyperlinks**: DOCX and PPTX image references now use
  `[![](path)](path)` syntax — the rendered image itself opens the file when
  clicked in any standard markdown viewer (VS Code, GitHub, Obsidian, …).
- **`scripts/batch_convert.py` + `batch_convert.bat`**: a CLI driver that
  scans a folder, converts every supported document to Markdown, and writes a
  timestamped log. Skips Office lock files (`~$*`) and previously-extracted
  `*_images/` directories so it's safe to re-run.
- **DOCX image extraction & embedding** (Roadmap item ✓). When `preserve_images=True`,
  every embedded picture is written to disk and the markdown output includes
  `![](path)` references at the image's original position in the document.
  Defaults to writing into `<source_stem>_images/` next to the source; can be
  overridden via `image_dir`.
- New `image_count` field in DOCX metadata.
- Unit tests for PDF, PPTX, Image (OCR), DOCX-image-extraction and the CLI —
  test count went from 15 → 41, coverage from 60 % → 88 %.
- CI workflow now runs `ruff format --check` and a separate `build` job that
  produces sdist + wheel and validates them with `twine check`.
- New `docs/claude-skills/` directory with the latest official Anthropic skill
  references (DOCX, PDF, PPTX) plus a curated OCR guide.

### Changed
- Renamed exception `FileNotFoundError_` → `MissingFileError` (proper PascalCase
  + `Error` suffix). The old name is gone — update imports accordingly.
- DOCX converter no longer emits the "Image extraction is not yet implemented"
  warning; image extraction is now real.
- `pyproject.toml`: added `[tool.ruff.lint.per-file-ignores]` for typer's B008
  pattern in `cli.py`, and `[[tool.mypy.overrides]]` to silence missing-stubs
  warnings for `pytesseract` / `pdfplumber` / `pptx`.

### Fixed
- CLI `formats` table: rich was interpreting `[pdf]/[pptx]/[ocr]` as markup
  tags and stripping them — escaped to render literally.
- `__all__` export list now sorted (RUF022 compliance).
- HTML converter: properly narrows BeautifulSoup attribute types
  (`str | list[str] | None`) before calling `.lower()`.
- PDF converter: removed duplicate inner `import pdfplumber` (F811).
- All trailing NUL-byte corruption removed from `pyproject.toml` and `README.md`.
- Repository identity: replaced placeholder `your-username` with `guru4tw`
  across pyproject URLs, CONTRIBUTING.md, README.md, and the
  `UnsupportedFormatError` issue link.

### Quality
- `ruff check`: ✅ all checks pass (was 10 warnings).
- `ruff format --check`: ✅ all 19 files formatted.
- `mypy --strict`: ✅ no issues in 11 source files (was 4 errors).
- `pytest`: ✅ 41 passed.
- Coverage: **88 %** overall; CLI 96 %, PDF 94 %, PPTX 89 %, OCR 86 %, HTML 87 %, DOCX 84 %.

## [0.1.0] - 2026-04-27

### Added
- Initial release 🧪
- DOCX → Markdown conversion with headings, lists, tables, and inline formatting
- HTML → Markdown conversion with metadata extraction
- PDF → Markdown conversion (text-based PDFs, optional `[pdf]` extra)
- PPTX → Markdown conversion with slides, bullets, and speaker notes (optional `[pptx]` extra)
- Image OCR via Tesseract (optional `[ocr]` extra)
- Friendly CLI with `rich`-powered error messages
- "Did you mean?" suggestions for typo'd filenames
- `Alchemist` class for advanced configuration
- `alchemize()` function for the simplest possible API
- Full type hints throughout
