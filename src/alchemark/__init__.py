"""
Alchemark — Transmute documents into Markdown gold.

Quick start:
    >>> import alchemark
    >>> markdown = alchemark.alchemize("report.docx")

Advanced:
    >>> from alchemark import Alchemist
    >>> alchemist = Alchemist(preserve_images=True)
    >>> result = alchemist.transmute("report.docx")
    >>> print(result.markdown)
"""

from alchemark.core import Alchemist, Result, alchemize
from alchemark.exceptions import (
    AlchemarkError,
    ConversionError,
    UnsupportedFormatError,
)

__version__ = "0.1.0"
__all__ = [
    "AlchemarkError",
    "Alchemist",
    "ConversionError",
    "Result",
    "UnsupportedFormatError",
    "alchemize",
]
