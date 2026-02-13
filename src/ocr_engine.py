"""OCR engine module using EasyOCR for text extraction from business cards."""

from typing import List, Optional, Dict, Any
import easyocr
from src.utils import logger, OCR_LANGUAGES

_reader: Optional[easyocr.Reader] = None


def get_reader() -> easyocr.Reader:
    """Get or create a singleton EasyOCR reader instance.

    Returns:
        easyocr.Reader: The EasyOCR reader instance.
    """
    global _reader
    if _reader is None:
        logger.info("Initializing EasyOCR reader with languages: %s", OCR_LANGUAGES)
        _reader = easyocr.Reader(OCR_LANGUAGES, gpu=False)
        logger.info("EasyOCR reader initialized successfully")
    return _reader


def extract_text(image_path: str) -> List[str]:
    """Extract text lines from a business card image using EasyOCR.

    Args:
        image_path: Path to the image file.

    Returns:
        List[str]: List of extracted text strings.
    """
    try:
        reader = get_reader()
        results = reader.readtext(image_path, detail=0, paragraph=False)
        text_lines = [line.strip() for line in results if line.strip()]
        logger.info("Extracted %d text lines from %s", len(text_lines), image_path)
        return text_lines
    except Exception as e:
        logger.error("OCR extraction failed for %s: %s", image_path, str(e))
        return []


def extract_text_with_confidence(image_path: str) -> List[Dict[str, Any]]:
    """Extract text with bounding boxes and confidence scores.

    Args:
        image_path: Path to the image file.

    Returns:
        List[Dict[str, Any]]: List of dicts with 'text', 'confidence', and 'bbox' keys.
    """
    try:
        reader = get_reader()
        results = reader.readtext(image_path)
        extracted = []
        for bbox, text, confidence in results:
            if text.strip():
                extracted.append({
                    "text": text.strip(),
                    "confidence": round(float(confidence), 4),
                    "bbox": bbox,
                })
        logger.info(
            "Extracted %d text segments with confidence from %s",
            len(extracted),
            image_path,
        )
        return extracted
    except Exception as e:
        logger.error(
            "OCR extraction with confidence failed for %s: %s", image_path, str(e)
        )
        return []
