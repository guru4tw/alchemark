# Contributing to Alchemark

Thanks for your interest in helping turn documents into Markdown gold! 🧪

## Getting Started

```bash
git clone https://github.com/guru4tw/alchemark
cd alchemark
pip install -e ".[dev,all]"
pre-commit install
```

## Running checks

```bash
pytest                # tests
ruff check .          # lint
ruff format .         # format
mypy src              # type-check
```

## Adding a new converter

Each format lives in `src/alchemark/converters/`. To add a new one:

1. Create `src/alchemark/converters/yourformat.py`.
2. Subclass `BaseConverter`, set `extensions = [".ext"]` and `name = "yourformat"`.
3. Implement `convert(self, path) -> Result`.
4. Register it in `Alchemist._register_builtin_converters()`.
5. If it needs new dependencies, add them as an optional extra in `pyproject.toml`
   and import lazily so missing dependencies don't break the core package.
6. Add tests under `tests/test_yourformat.py`.

## Style

- Follow PEP 8; `ruff` enforces this.
- Use type hints everywhere — this is a library and consumers rely on them.
- Friendly error messages: every `AlchemarkError` should include a `hint` whenever
  there's something actionable the user can do.

## Pull Requests

- Open an issue first for major changes.
- Keep PRs focused — one feature or fix per PR.
- Update `CHANGELOG.md` under `[Unreleased]`.
