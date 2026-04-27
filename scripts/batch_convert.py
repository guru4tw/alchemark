#!/usr/bin/env python3
"""Batch convert documents in a directory to Markdown using Alchemark.

Examples
--------
# Convert every supported file in the current dir into ./md, log into ./log:
$ python batch_convert.py

# Convert only files inside ~/docs, output into ~/docs/markdown:
$ python batch_convert.py -i ~/docs -o ~/docs/markdown

# Recurse into subdirectories and preserve embedded images for DOCX:
$ python batch_convert.py -r --preserve-images

The script:
  * Discovers every file in INPUT whose extension Alchemark currently supports.
  * Converts each one and writes ``<stem>.md`` into OUTPUT (preserving the
    sub-folder structure when ``--recursive`` is used).
  * Writes a timestamped log file under LOG with full per-file detail.
  * Prints a final summary listing every output file, its size, and any
    failures, then exits with status 0 if everything succeeded, 1 otherwise.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from alchemark import Alchemist
    from alchemark.exceptions import AlchemarkError
except ImportError as e:  # pragma: no cover
    sys.stderr.write(
        "ERROR: alchemark is not installed. From the project root run:\n"
        "    pip install -e .[all]\n"
        f"\n(import error: {e})\n"
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def setup_logger(log_dir: Path, quiet: bool) -> tuple[logging.Logger, Path]:
    """Configure a logger that writes to both a timestamped file and stdout."""
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"batch_convert_{timestamp}.log"

    logger = logging.getLogger("alchemark.batch")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)

    if not quiet:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(console)

    return logger, log_file


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def discover_files(
    input_dir: Path,
    supported: set[str],
    recursive: bool,
    excluded_dirs: list[Path],
) -> list[Path]:
    """Return every file under ``input_dir`` that has a supported extension.

    Files inside any of ``excluded_dirs`` are skipped to avoid recursively
    converting our own outputs and log files.
    """
    pattern = "**/*" if recursive else "*"
    files: list[Path] = []
    excluded_resolved = [d.resolve() for d in excluded_dirs]
    for p in input_dir.glob(pattern):
        if not p.is_file():
            continue
        if p.suffix.lower() not in supported:
            continue
        # Skip Microsoft Office lock files (~$file.docx)
        if p.name.startswith("~$"):
            continue
        # Skip files inside any directory whose name ends with "_images" — those
        # are typically outputs from a previous --preserve-images run; we don't
        # want to re-OCR our own extracted pictures.
        if any(parent.name.endswith("_images") for parent in p.parents):
            continue
        try:
            resolved = p.resolve()
        except OSError:
            continue
        if any(_is_within(resolved, ex) for ex in excluded_resolved):
            continue
        files.append(p)
    return sorted(files)


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------


def convert_one(
    alchemist: Alchemist,
    src: Path,
    target: Path,
    logger: logging.Logger,
) -> tuple[bool, int, float, list[str]]:
    """Convert a single file. Returns (success, bytes_written, seconds, warnings)."""
    target.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    try:
        result = alchemist.transmute(src)
        result.save(target)
    except AlchemarkError as e:
        logger.error(f"  ✗ {src.name}: {e.message}")
        if e.hint:
            for line in e.hint.splitlines():
                logger.error(f"      {line.strip()}")
        return False, 0, time.perf_counter() - t0, []
    except Exception as e:
        logger.error(f"  ✗ {src.name}: unexpected {type(e).__name__}: {e}")
        return False, 0, time.perf_counter() - t0, []
    elapsed = time.perf_counter() - t0
    size = target.stat().st_size
    return True, size, elapsed, list(result.warnings)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="batch_convert.py",
        description="Batch-convert documents to Markdown using Alchemark.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path.cwd(),
        help="Directory to scan for input files.",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Where to write .md files. Defaults to <input>/md.",
    )
    p.add_argument(
        "-l",
        "--log-dir",
        type=Path,
        default=None,
        help="Where to write the run log. Defaults to <input>/log.",
    )
    p.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recurse into sub-directories.",
    )
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress console output (log file is still written).",
    )
    p.add_argument(
        "--preserve-images",
        action="store_true",
        help="Extract embedded images (DOCX only).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    input_dir = args.input.expanduser().resolve()
    if not input_dir.is_dir():
        sys.stderr.write(f"ERROR: input path is not a directory: {input_dir}\n")
        return 2

    output_dir = (args.output or input_dir / "md").expanduser().resolve()
    log_dir = (args.log_dir or input_dir / "log").expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    logger, log_file = setup_logger(log_dir, args.quiet)

    alchemist = Alchemist(preserve_images=args.preserve_images)
    supported = set(alchemist.supported_extensions)

    logger.info("=" * 70)
    logger.info("Alchemark batch conversion")
    logger.info("=" * 70)
    logger.info(f"  Input dir       : {input_dir}")
    logger.info(f"  Output dir      : {output_dir}")
    logger.info(f"  Log file        : {log_file}")
    logger.info(f"  Recursive       : {args.recursive}")
    logger.info(f"  Preserve images : {args.preserve_images}")
    logger.info(f"  Supported exts  : {', '.join(sorted(supported))}")
    logger.info("")

    files = discover_files(
        input_dir,
        supported,
        args.recursive,
        excluded_dirs=[output_dir, log_dir],
    )
    logger.info(f"Found {len(files)} convertible file(s).")

    if not files:
        logger.warning("Nothing to do.")
        return 0

    succeeded: list[tuple[Path, Path, int, float]] = []
    failed: list[Path] = []

    overall_t0 = time.perf_counter()
    logger.info("")
    logger.info("Converting:")
    for src in files:
        # Mirror sub-directory layout under output_dir.
        try:
            rel_parent = src.parent.resolve().relative_to(input_dir)
        except ValueError:
            rel_parent = Path()
        target = output_dir / rel_parent / f"{src.stem}.md"

        ok, size, dt, warnings = convert_one(alchemist, src, target, logger)
        if ok:
            logger.info(
                f"  ✓ {src.relative_to(input_dir)} → {target.relative_to(output_dir.parent)} ({size:,} bytes, {dt * 1000:.0f} ms)"
            )
            for w in warnings:
                logger.warning(f"      ⚠ {w}")
            succeeded.append((src, target, size, dt))
        else:
            failed.append(src)

    overall_elapsed = time.perf_counter() - overall_t0

    # ---- Summary ----
    logger.info("")
    logger.info("=" * 70)
    logger.info(
        f"Summary: {len(succeeded)} succeeded, {len(failed)} failed, {overall_elapsed:.2f}s total"
    )
    logger.info("=" * 70)

    if succeeded:
        total_bytes = sum(s for _, _, s, _ in succeeded)
        logger.info("")
        logger.info("Output files:")
        for _, target, size, _dt in succeeded:
            logger.info(f"  {target}  ({size:,} bytes)")
        logger.info(f"  ── total: {total_bytes:,} bytes across {len(succeeded)} file(s)")

    if failed:
        logger.info("")
        logger.info("Failed files:")
        for src in failed:
            logger.info(f"  {src}")

    logger.info("")
    logger.info(f"Output dir : {output_dir}")
    logger.info(f"Log file   : {log_file}")

    return 0 if not failed else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
