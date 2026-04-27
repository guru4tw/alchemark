# Scripts

Command-line utilities that ship alongside the Alchemark library.

## `batch_convert.py` / `batch_convert.bat` — bulk document → Markdown

Convert every supported document in a folder to Markdown in one shot, with
per-run logging.

### Defaults

| Setting | Default |
|---|---|
| Input dir | current working dir |
| Output dir | `<input>/md` |
| Log dir | `<input>/log` (timestamped `batch_convert_YYYYMMDD_HHMMSS.log`) |
| Recursive | off (`--recursive` to enable) |
| Preserve images | off (`--preserve-images` to enable) |

### Usage (Linux / macOS)

```bash
python scripts/batch_convert.py                              # cwd → ./md
python scripts/batch_convert.py -i ~/docs -o ~/docs/markdown # custom paths
python scripts/batch_convert.py -r --preserve-images         # recursive + images
```

### Usage (Windows)

The `.bat` wrapper sets UTF-8 codepage (so 中文 filenames work), auto-detects
your Python interpreter, and forwards extra flags:

```cmd
scripts\batch_convert.bat                       REM scan current dir
scripts\batch_convert.bat C:\path\to\folder     REM scan specific folder
scripts\batch_convert.bat C:\in -o C:\out -q    REM forward more flags
```

Defaults applied by the .bat: `--recursive --preserve-images`.

### Flags

| Flag | Description |
|---|---|
| `-i / --input` | Folder to scan |
| `-o / --output` | Where to write `.md` files (folder mirrors input layout when `-r`) |
| `-l / --log-dir` | Where to write the run log |
| `-r / --recursive` | Walk sub-directories |
| `-q / --quiet` | Suppress console output (log file is still written) |
| `--preserve-images` | DOCX/PPTX — extract pictures and reference them in markdown |

### Output

For every successful conversion the script writes `<stem>.md` to the output
dir. Subfolder layout is preserved when `--recursive` is used.

The console + log file both contain:

* Configuration banner (input/output/log paths, supported extensions)
* One ✓/✗ line per file, with size and elapsed time
* Per-file warnings (e.g. PDF page with no extractable text)
* Final summary: success/failure counts, total elapsed time, total bytes
* Full list of every output file path with size

### Exit codes

* `0` — every file converted successfully (or none were found)
* `1` — at least one conversion failed
* `2` — invalid input directory or alchemark not installed

---

## `push_to_github.bat` — one-shot uploader to `guru4tw/alchemark`

Initialises git, makes the initial commit + tag, configures the remote, and
pushes `main` + `v0.1.0` to GitHub. Idempotent — safe to re-run; it skips
steps that are already done.

### Prerequisites

1. **git** installed and on PATH (https://git-scm.com/download/win).
2. The **empty** repo already created on GitHub:
   - Go to https://github.com/new
   - Owner = `guru4tw`, Name = `alchemark`
   - Do **not** tick "Initialize with README / .gitignore / License" — those
     are already in this project.
3. A **GitHub Personal Access Token** (PAT) for authentication:
   - https://github.com/settings/tokens?type=beta
   - Repository access → only this repo
   - Permission → Contents = Read and write
   - Username when prompted: `guru4tw`, password = the PAT.

### Usage

```cmd
scripts\push_to_github.bat
```

Walks through six steps, prints a summary at each, and asks for confirmation
before the actual `git push`.

### What it cleans up before committing

To keep the upload tiny and free of churn, the script first removes:

- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `build/`, `dist/`, `*.bundle`, `*.coverage*`
- Recursively: any `__pycache__/` and any `*_images/` folders produced by
  previous `--preserve-images` runs
- `docs/claude-skills/` — Anthropic's proprietary skill docs (must NOT be
  pushed publicly)

### Re-pointing the remote

If `origin` is already configured to a different URL the script silently
re-points it to `https://github.com/guru4tw/alchemark.git`.

### After a successful push

- View the repo: https://github.com/guru4tw/alchemark
- The CI workflow (`.github/workflows/ci.yml`) will start running automatically
- To publish to PyPI, create a Release v0.1.0 on GitHub — `publish.yml` does
  the rest via Trusted Publishing
