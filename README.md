# 📇 Business Card Intelligence System

A smart OCR-powered web application that extracts contact information from business card images using advanced computer vision and natural language processing.

## ✨ Features

- **🖼️ Multi-format Support**: Upload JPG, PNG, WebP, and other image formats
- **🔍 Advanced OCR**: Uses EasyOCR for accurate text extraction
- **📝 Entity Recognition**: Automatically identifies names, emails, phone numbers, companies, and more
- **✏️ Editable Results**: Review and edit extracted information before export
- **📊 Excel Export**: Download extracted data as formatted Excel spreadsheets
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🚀 Live Demo

**[🌐 Try the Live Application](https://huggingface.co/spaces/23f1002381/business-card-intelligence)**

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **OCR Engine**: EasyOCR
- **Image Processing**: PIL (Pillow)
- **Data Export**: OpenPyXL
- **Backend**: Python 3.11+

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/23f1002381/ML-Assistant.git
cd ML-Assistant
```

2. Install dependencies:
```bash
pip install streamlit easyocr openpyxl Pillow
```

3. Run the application:
```bash
streamlit run app.py
```

## 🎯 How to Use

1. **Upload Images**: Drag and drop business card images or click to browse
2. **Extract Information**: Click "Extract Information" to process the cards
3. **Review Results**: Check extracted data and make any necessary edits
4. **Export Data**: Download the results as an Excel file

## 📁 Project Structure

```
ML-Assistant/
├── app.py                 # Main Streamlit application
├── src/
│   ├── image_processor.py # Image preprocessing
│   ├── ocr_engine.py      # OCR text extraction
│   ├── entity_baseline.py # Entity recognition
│   ├── excel_exporter.py  # Excel export functionality
│   └── utils.py          # Utility functions
├── uploads/              # Temporary upload directory
├── output/               # Generated output files
└── pyproject.toml        # Project dependencies
```

## 🌟 Deployment

### Hugging Face Spaces (Recommended)

The application is deployed on Hugging Face Spaces for free hosting:

**[🚀 Deploy to Hugging Face Spaces](https://huggingface.co/new-space?template=23f1002381/business-card-intelligence)**

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py --server.port 8501
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- **GitHub Repository**: https://github.com/23f1002381/ML-Assistant
- **Live Demo**: https://huggingface.co/spaces/23f1002381/business-card-intelligence
- **Issues**: https://github.com/23f1002381/ML-Assistant/issues

---

Made with ❤️ using Streamlit and EasyOCR
