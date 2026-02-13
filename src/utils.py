"""Utility functions and configuration for the Business Card Intelligence System."""

import os
import logging
from pathlib import Path
from typing import Dict, Any

UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
MAX_UPLOAD_COUNT: int = 20
SUPPORTED_EXTENSIONS: tuple = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")
OCR_LANGUAGES: list = ["en"]
DEFAULT_EXCEL_FILENAME: str = "extracted_cards.xlsx"

ENTITY_FIELDS: list = [
    "Name",
    "Company",
    "Designation",
    "Phone",
    "Email",
    "Website",
    "Address",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger: logging.Logger = logging.getLogger("BusinessCardML")


def ensure_directories() -> None:
    """Create required directories if they do not exist."""
    for directory in [UPLOAD_DIR, OUTPUT_DIR]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    logger.info("Directories verified: %s, %s", UPLOAD_DIR, OUTPUT_DIR)


def get_empty_entity_dict() -> Dict[str, str]:
    """Return a dictionary with all entity fields initialized to empty strings.

    Returns:
        Dict[str, str]: Dictionary with entity field names as keys.
    """
    return {field: "" for field in ENTITY_FIELDS}


def validate_file_extension(filename: str) -> bool:
    """Check if a file has a supported image extension.

    Args:
        filename: The name of the file to validate.

    Returns:
        bool: True if the extension is supported, False otherwise.
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_EXTENSIONS


def sanitize_text(text: str) -> str:
    """Clean and normalize extracted text.

    Args:
        text: Raw text string to sanitize.

    Returns:
        str: Cleaned text string.
    """
    if not text:
        return ""
    text = text.strip()
    text = " ".join(text.split())
    return text
