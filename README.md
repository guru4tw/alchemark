<div align="center">

# 🧪 Alchemark

**Transmute documents into Markdown gold.**

*The Pythonic document-to-Markdown library — beautiful API, helpful errors, zero surprises.*

[![PyPI version](https://img.shields.io/pypi/v/alchemark.svg)](https://pypi.org/project/alchemark/)
[![Python versions](https://img.shields.io/pypi/pyversions/alchemark.svg)](https://pypi.org/project/alchemark/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/guru4tw/alchemark/actions/workflows/ci.yml/badge.svg)](https://github.com/guru4tw/alchemark/actions/workflows/ci.yml)

</div>

---

## ✨ Why Alchemark?

There are plenty of "doc-to-markdown" tools out there. Alchemark is opinionated about three things:

- 🪶 **A library first.** Clean, type-hinted Python API. The CLI is a thin wrapper.
- 🔮 **Helpful errors.** Did you typo a filename? We'll tell you what you probably meant. Missing a dependency? We'll tell you exactly what to install.
- 🧩 **Pluggable.** Each format is a converter module. Adding new ones is one file.

## 📦 Installation

```bash
pip install alchemark
```

That's it — every converter (DOCX, HTML, PDF, PPTX, image OCR) is bundled by default.

> **Note:** image OCR additionally needs the **Tesseract binary** on PATH:
> ```bash
> # macOS:   brew install tesseract
> # Ubuntu:  sudo apt-get install tesseract-ocr
> # Windows: choco install tesseract
> ```

## 🚀 Quick Start

### Library

```python
import alchemark

# Simplest possible: file in, markdown out.
markdown = alchemark.alchemize("report.docx")
print(markdown)
```

### Advanced

```python
from alchemark import Alchemist

alchemist = Alchemist(
    preserve_images=True,
    image_dir="./images",
    on_warning=lambda w: print(f"⚠ {w}"),
)

result = alchemist.transmute("report.docx")
print(result.markdown)
print(result.metadata)   # {'title': '...', 'author': '...', ...}
print(result.warnings)   # non-fatal issues, e.g. unsupported features

# Save directly:
result.save("report.md")
```

### Batch

```python
from alchemark import Alchemist

alchemist = Alchemist()
for result in alchemist.transmute_all("./docs/*.docx"):
    result.save(f"./out/{result.source.stem}.md")
```

### CLI

```bash
# Convert and write to file
alchemark convert report.docx -o report.md

# Pipe to stdout
alchemark convert report.html | less

# See what formats are available
alchemark formats
```

## 🎨 Friendly Errors

Typo a filename? You get suggestions, not stack traces:

```
❌ Alchemark Error
Cannot find 'reprot.docx'

  Hint: Did you mean: report.docx?
        Working directory: /Users/you/projects
        Tip: Use absolute paths to avoid ambiguity.
```

Missing an optional dependency? You're told exactly what to install:

```
❌ Alchemark Error
Unsupported file format: .pdf (report.pdf)

  Hint: Supported formats: .docx, .html, .htm.
        Install PDF support with: pip install alchemark[pdf]
```

## 📋 Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Word | `.docx` | with image extraction & embedding |
| HTML | `.html`, `.htm` | with metadata extraction |
| PDF | `.pdf` | text-based PDFs |
| PowerPoint | `.pptx` | with image extraction & embedding |
| Images (OCR) | `.png`, `.jpg`, `.tiff`, ... | needs Tesseract binary |

## 🛠 Development

```bash
git clone https://github.com/guru4tw/alchemark
cd alchemark
pip install -e ".[dev,all]"

pytest                    # run tests
ruff check .              # lint
ruff format .             # format
mypy src                  # type-check
```

## 🗺 Roadmap

- [x] DOCX
- [x] HTML
- [x] PDF (text-based)
- [x] PPTX
- [x] Image OCR
- [x] Image extraction & embedding for DOCX and PPTX
- [ ] EPUB
- [ ] RTF
- [ ] Async API
- [ ] Streaming for huge files

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss major changes.

## 📜 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

*Like medieval alchemists turning lead into gold, Alchemark turns your documents into Markdown.*

</div>
