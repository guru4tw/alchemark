# CLAUDE.md — Alchemark

> 文件轉 Markdown 的 Python 函式庫(DOCX / HTML / PDF / PPTX / 圖片 OCR),已發布 PyPI,MIT。
> 使用說明見 [README.md](README.md);開發流程與新增 converter 步驟見 [CONTRIBUTING.md](CONTRIBUTING.md);版本紀錄 [CHANGELOG.md](CHANGELOG.md)。

## 結構

- `src/alchemark/core.py` — `Alchemist` 主 API,`_register_builtin_converters()` 註冊所有格式
- `src/alchemark/converters/` — 一格式一檔,繼承 `base.py` 的 `BaseConverter`
- `src/alchemark/cli.py` — typer CLI,只是 API 的薄殼,邏輯不放這裡
- `src/alchemark/exceptions.py` — `AlchemarkError`,可行動的錯誤一律帶 `hint`
- `scripts/` — 批次轉檔與推 GitHub 的工具腳本(見 `scripts/README.md`)

## 指令

```bash
pip install -e ".[dev]"
pytest
ruff check . && ruff format .
mypy src
```

## 紀律

- 函式庫優先:公開 API 全部 type hint;CLI 不加 API 沒有的功能。
- 所有 converter 依賴都已放進必裝 `dependencies`;`[pdf]`/`[pptx]`/`[ocr]`/`[all]` extras 只是為相容保留的空別名,不要刪。(CONTRIBUTING 第 5 步「新依賴放 optional extra」與此現況不符,以此為準。)
- 圖片 OCR 另需系統裝 Tesseract binary,測試環境沒有時相關測試應 skip 而非失敗。
- 改動要在 `CHANGELOG.md` 的 `[Unreleased]` 記一筆。
- `.pypirc` 不入版控;發布 PyPI 屬對外動作,需使用者明確同意。
