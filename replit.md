# Smart Business Card Intelligence System

## Overview
OCR-based business card information extraction system using EasyOCR, regex/heuristics entity extraction, and Excel export. Built with Streamlit.

## Current Phase
Phase 1 — Basic Working System (Complete)

## Project Structure
```
├── app.py                    # Streamlit UI
├── src/
│   ├── utils.py              # Config, logging, utility functions
│   ├── image_processor.py    # Image preprocessing (grayscale, contrast, sharpen)
│   ├── ocr_engine.py         # EasyOCR text extraction (singleton reader)
│   ├── entity_baseline.py    # Regex + heuristics entity extraction
│   └── excel_exporter.py     # Excel export with openpyxl
├── uploads/                  # Temporary uploaded images
├── output/                   # Generated Excel files
```

## Key Technical Details
- **OCR**: EasyOCR (CPU-only, English)
- **Entity fields**: Name, Company, Designation, Phone, Email, Website, Address
- **Export**: .xlsx with styled headers, auto-filter
- **Max uploads**: 20 images per session
- **Supported formats**: PNG, JPG, JPEG, BMP, TIFF, WEBP

## Running
```
streamlit run app.py --server.port 5000
```

## Dependencies
- streamlit, easyocr, openpyxl, Pillow
- Python >=3.11,<3.12 (easyocr compatibility)
