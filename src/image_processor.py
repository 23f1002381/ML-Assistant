"""Image processing module for business card images."""

import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
from src.utils import logger, UPLOAD_DIR, validate_file_extension


def save_uploaded_image(uploaded_file: any, filename: str) -> Optional[str]:
    """Save an uploaded file to the uploads directory.

    Args:
        uploaded_file: The file object from Streamlit uploader.
        filename: The original filename.

    Returns:
        Optional[str]: The full path to the saved file, or None on failure.
    """
    if not validate_file_extension(filename):
        logger.warning("Unsupported file extension: %s", filename)
        return None

    try:
        safe_filename = Path(filename).name
        filepath = os.path.join(UPLOAD_DIR, safe_filename)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info("Saved uploaded image: %s", filepath)
        return filepath
    except Exception as e:
        logger.error("Failed to save image %s: %s", filename, str(e))
        return None


def preprocess_image(image_path: str) -> Optional[str]:
    """Preprocess a business card image for better OCR results.

    Applies grayscale conversion, contrast enhancement, and sharpening.

    Args:
        image_path: Path to the input image.

    Returns:
        Optional[str]: Path to the preprocessed image, or None on failure.
    """
    try:
        img = Image.open(image_path)
        img = img.convert("L")
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        img = img.filter(ImageFilter.SHARPEN)
        processed_path = os.path.splitext(image_path)[0] + "_processed.png"
        img.save(processed_path)
        logger.info("Preprocessed image saved: %s", processed_path)
        return processed_path
    except Exception as e:
        logger.error("Image preprocessing failed for %s: %s", image_path, str(e))
        return None


def get_image_dimensions(image_path: str) -> Optional[Tuple[int, int]]:
    """Get the dimensions of an image.

    Args:
        image_path: Path to the image file.

    Returns:
        Optional[Tuple[int, int]]: Width and height tuple, or None on failure.
    """
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        logger.error("Failed to get dimensions for %s: %s", image_path, str(e))
        return None


def cleanup_processed_images(directory: str) -> None:
    """Remove preprocessed image files from a directory.

    Args:
        directory: Path to the directory to clean.
    """
    try:
        for filename in os.listdir(directory):
            if filename.endswith("_processed.png"):
                filepath = os.path.join(directory, filename)
                os.remove(filepath)
                logger.info("Cleaned up: %s", filepath)
    except Exception as e:
        logger.error("Cleanup failed: %s", str(e))
