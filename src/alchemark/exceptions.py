"""Alchemark exceptions with helpful hints."""

from __future__ import annotations

from pathlib import Path


class AlchemarkError(Exception):
    """Base exception for all Alchemark errors.

    Every Alchemark error carries an optional `hint` attribute that suggests
    how to fix the problem. CLI mode renders these hints with rich formatting;
    library users can access `error.hint` directly.
    """

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint

    def __str__(self) -> str:
        if self.hint:
            return f"{self.message}\n\n  Hint: {self.hint}"
        return self.message


class UnsupportedFormatError(AlchemarkError):
    """Raised when the input file format is not supported."""

    def __init__(self, path: Path, supported: list[str]) -> None:
        ext = path.suffix.lower() or "(no extension)"
        message = f"Unsupported file format: {ext} ({path.name})"
        hint = (
            f"Supported formats: {', '.join(supported)}.\n"
            f"  If you need {ext} support, please open an issue at:\n"
            f"  https://github.com/guru4tw/alchemark/issues"
        )
        super().__init__(message, hint)
        self.path = path
        self.supported = supported


class ConversionError(AlchemarkError):
    """Raised when conversion fails for a reason specific to the document."""

    def __init__(self, path: Path, reason: str, hint: str | None = None) -> None:
        message = f"Failed to convert '{path.name}': {reason}"
        super().__init__(message, hint)
        self.path = path
        self.reason = reason


class MissingFileError(AlchemarkError):
    """Raised when the input file doesn't exist. Includes 'did you mean' hints."""

    def __init__(self, path: Path, suggestions: list[Path] | None = None) -> None:
        message = f"Cannot find '{path}'"
        hint_lines = []
        if suggestions:
            names = ", ".join(s.name for s in suggestions[:3])
            hint_lines.append(f"Did you mean: {names}?")
        hint_lines.append(
            f"Working directory: {Path.cwd()}\n  Tip: Use absolute paths to avoid ambiguity."
        )
        super().__init__(message, "\n  ".join(hint_lines))
        self.path = path


class MissingDependencyError(AlchemarkError):
    """Raised when an optional dependency is needed but not installed."""

    def __init__(self, feature: str, extra: str, package: str) -> None:
        message = f"The '{feature}' feature requires the '{package}' package."
        hint = (
            f"Install it with:\n"
            f"      pip install alchemark[{extra}]\n"
            f"    Or directly:\n"
            f"      pip install {package}"
        )
        super().__init__(message, hint)
