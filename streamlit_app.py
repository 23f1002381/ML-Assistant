"""Smart Business Card Intelligence System — Streamlit Application."""

import streamlit as st
import os
import tempfile
from PIL import Image
import re
import pandas as pd
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Business Card Intelligence",
    page_icon="📇",
    layout="wide",
)

# Constants
ENTITY_FIELDS = ["Name", "Title", "Company", "Email", "Phone", "Address", "Website"]
MAX_UPLOAD_COUNT = 10
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']

# Initialize OCR reader with error handling
@st.cache_resource
def load_ocr_reader():
    try:
        import easyocr
        with st.spinner("Loading OCR engine..."):
            reader = easyocr.Reader(['en'])
        return reader
    except Exception as e:
        st.error(f"Error loading OCR: {e}")
        return None

# Mock OCR for testing when real OCR fails
def mock_ocr_extract(image_path):
    """Mock OCR function for testing"""
    import random
    sample_texts = [
        """John Doe
Software Engineer
Tech Company Inc.
john.doe@techcompany.com
+1 (555) 123-4567
123 Tech Street, Silicon Valley, CA 94000
www.techcompany.com""",
        """Jane Smith
Marketing Director
Creative Agency
jane.smith@creative.com
+1 (555) 987-6543
456 Design Ave, New York, NY 10001""",
        """Robert Johnson
CEO
Startup Ventures
robert.j@startup.io
+1 (555) 246-8135
789 Innovation Blvd, Austin, TX 73301
www.startup.io"""
    ]
    return random.choice(sample_texts).split('\n')

# Extract text using OCR
def extract_text(image_path, reader):
    try:
        if reader is None:
            st.warning("Using mock OCR for demo. Real OCR not available.")
            return mock_ocr_extract(image_path)
        
        results = reader.readtext(image_path)
        text_lines = [text[1] for text in results]
        return text_lines
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return mock_ocr_extract(image_path)

# Extract entities from text
def extract_entities(text_lines):
    entities = {field: "" for field in ENTITY_FIELDS}
    
    # Combine all text
    full_text = " ".join(text_lines)
    
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, full_text)
    if emails:
        entities["Email"] = emails[0]
    
    # Phone extraction
    phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phones = re.findall(phone_pattern, full_text)
    if phones:
        phone = phones[0]
        formatted_phone = f"({phone[1]}) {phone[2]}-{phone[3]}"
        if phone[0]:  # Has country code
            formatted_phone = phone[0] + " " + formatted_phone
        entities["Phone"] = formatted_phone
    
    # Website extraction
    website_pattern = r'(https?://)?(www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    websites = re.findall(website_pattern, full_text)
    if websites:
        website = websites[0]
        if website[0] or website[1]:
            entities["Website"] = f"{website[0] or ''}{website[1] or ''}{website[2] or ''}"
    
    # Extract name, title, company (heuristic approach)
    for i, line in enumerate(text_lines):
        line = line.strip()
        if not line:
            continue
            
        # Name (usually first line with 2-3 words)
        if not entities["Name"] and i < 2 and len(line.split()) <= 3:
            if not re.match(email_pattern, line) and not re.match(phone_pattern, line):
                entities["Name"] = line
        
        # Title (contains common title keywords)
        elif not entities["Title"] and any(keyword in line.lower() for keyword in 
                                         ['ceo', 'cto', 'president', 'director', 'manager', 'engineer', 
                                          'developer', 'designer', 'consultant', 'analyst']):
            entities["Title"] = line
        
        # Company (contains company indicators)
        elif not entities["Company"] and any(indicator in line.lower() for indicator in
                                            ['inc', 'corp', 'llc', 'ltd', 'co', 'company', 'corporation']):
            entities["Company"] = line
        
        # Address (contains address patterns)
        elif not entities["Address"] and re.search(r'\d+\s+\w+\s+(?:street|st|avenue|ave|boulevard|blvd)', line.lower()):
            entities["Address"] = line
    
    return entities

# Export to Excel
def export_to_excel_bytes(data):
    try:
        df = pd.DataFrame(data)
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Business Cards')
        excel_buffer.seek(0)
        return excel_buffer.getvalue()
    except Exception as e:
        st.error(f"Error creating Excel file: {e}")
        return None

# Main app
def main():
    # Custom CSS
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2rem;
            font-weight: 700;
            color: #2F5496;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1rem;
            color: #666;
            margin-bottom: 2rem;
        }
        .card-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid #e0e0e0;
        }
        .stButton>button {
            background-color: #2F5496;
            color: white;
            border-radius: 6px;
            padding: 0.5rem 2rem;
        }
        .ocr-status {
            background: #fff3cd;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #ffeaa7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="main-header">📇 Business Card Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload business card images to extract contact information using OCR</div>', unsafe_allow_html=True)

    # OCR Status
    st.markdown('<div class="ocr-status">ℹ️ <strong>Status:</strong> OCR engine loading... This may take a moment on first run.</div>', unsafe_allow_html=True)

    # Load OCR reader
    reader = load_ocr_reader()
    if reader is not None:
        st.success("✅ OCR engine loaded successfully!")
    else:
        st.warning("⚠️ Using demo mode with mock OCR data")

    # Session state
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = []
    if "processing_done" not in st.session_state:
        st.session_state.processing_done = False

    # File upload
    extensions_str = ", ".join(SUPPORTED_EXTENSIONS)
    uploaded_files = st.file_uploader(
        f"Upload business card images (max {MAX_UPLOAD_COUNT})",
        type=[ext.replace(".", "") for ext in SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
        help=f"Supported formats: {extensions_str}",
    )

    if uploaded_files and len(uploaded_files) > MAX_UPLOAD_COUNT:
        st.warning(f"Maximum {MAX_UPLOAD_COUNT} images allowed. Only the first {MAX_UPLOAD_COUNT} will be processed.")
        uploaded_files = uploaded_files[:MAX_UPLOAD_COUNT]

    if uploaded_files:
        process_btn = st.button("🔍 Extract Information", type="primary", use_container_width=True)

        if process_btn:
            st.session_state.extracted_data = []
            st.session_state.processing_done = False

            progress_bar = st.progress(0)
            status_text = st.empty()

            total = len(uploaded_files)
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing card {idx + 1} of {total}: {uploaded_file.name}")
                progress_bar.progress((idx) / total)

                try:
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name

                    # Extract text
                    text_lines = extract_text(tmp_path, reader)
                    if not text_lines:
                        st.warning(f"No text detected in: {uploaded_file.name}")
                        entities = {field: "" for field in ENTITY_FIELDS}
                    else:
                        entities = extract_entities(text_lines)

                    entities["_source_file"] = uploaded_file.name
                    entities["_raw_text"] = "\n".join(text_lines)
                    st.session_state.extracted_data.append(entities)

                    # Cleanup
                    os.unlink(tmp_path)

                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
                    # Add empty entry for failed processing
                    entities = {field: "" for field in ENTITY_FIELDS}
                    entities["_source_file"] = uploaded_file.name
                    entities["_raw_text"] = f"Error: {e}"
                    st.session_state.extracted_data.append(entities)

            progress_bar.progress(1.0)
            status_text.text("Processing complete!")
            st.session_state.processing_done = True

    # Display results
    if st.session_state.processing_done and st.session_state.extracted_data:
        st.divider()
        st.subheader("📋 Extracted Information")

        for card_idx, card_data in enumerate(st.session_state.extracted_data):
            source_file = card_data.get("_source_file", f"Card {card_idx + 1}")
            raw_text = card_data.get("_raw_text", "")

            with st.expander(f"Card {card_idx + 1}: {source_file}", expanded=(card_idx == 0)):
                col_img, col_data = st.columns([1, 2])

                with col_img:
                    matching_file = None
                    if uploaded_files:
                        for uf in uploaded_files:
                            if uf.name == source_file:
                                matching_file = uf
                                break
                    if matching_file:
                        st.image(matching_file, caption=source_file, use_container_width=True)

                    if raw_text:
                        with st.popover("👁️ View Raw OCR Text"):
                            st.text(raw_text)

                with col_data:
                    edited_values = {}
                    for field in ENTITY_FIELDS:
                        edited_values[field] = st.text_input(
                            field,
                            value=card_data.get(field, ""),
                            key=f"card_{card_idx}_{field}",
                        )
                    st.session_state.extracted_data[card_idx].update(edited_values)

        st.divider()

        # Export section
        export_data = []
        for card in st.session_state.extracted_data:
            clean_card = {field: card.get(field, "") for field in ENTITY_FIELDS}
            export_data.append(clean_card)

        excel_bytes = export_to_excel_bytes(export_data)
        if excel_bytes:
            st.download_button(
                label="📊 Download Excel Report",
                data=excel_bytes,
                file_name="business_cards_extracted.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )

        st.divider()
        st.subheader("📊 Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cards Processed", len(st.session_state.extracted_data))
        with col2:
            emails_found = sum(1 for c in st.session_state.extracted_data if c.get("Email"))
            st.metric("Emails Found", emails_found)
        with col3:
            phones_found = sum(1 for c in st.session_state.extracted_data if c.get("Phone"))
            st.metric("Phones Found", phones_found)

if __name__ == "__main__":
    main()
