"""Smart Business Card Intelligence System — Streamlit Application."""

import streamlit as st
from PIL import Image
from src.utils import ensure_directories, ENTITY_FIELDS, MAX_UPLOAD_COUNT, SUPPORTED_EXTENSIONS, logger
from src.image_processor import preprocess_image, save_uploaded_image, cleanup_processed_images
from src.ocr_engine import extract_text
from src.entity_baseline import extract_entities
from src.excel_exporter import export_to_excel_bytes

ensure_directories()

st.set_page_config(
    page_title="Business Card Intelligence",
    page_icon="📇",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Global Styles */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
        text-align: center;
        letter-spacing: -0.025em;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #4b5563;
        margin-bottom: 2.5rem;
        text-align: center;
        font-weight: 400;
    }
    
    /* Card Container */
    .card-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(229, 231, 235, 0.5);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out;
    }
    
    .card-container:hover {
        transform: translateY(-2px);
    }
    
    /* Input Styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        padding: 0.6rem;
    }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(to right, #2563eb, #1e40af);
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton>button:hover {
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
        transform: translateY(-1px);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Metric Card Simulation */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        border-top: 4px solid #2563eb;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a8a;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        border: 2px dashed #cbd5e1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">Smart Business Card Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload business card images to extract contact information using OCR</div>', unsafe_allow_html=True)

if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = []
if "processing_done" not in st.session_state:
    st.session_state.processing_done = False

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
    process_btn = st.button("Extract Information", type="primary", use_container_width=True)

    if process_btn:
        st.session_state.extracted_data = []
        st.session_state.processing_done = False

        progress_bar = st.progress(0)
        status_text = st.empty()

        total = len(uploaded_files)
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing card {idx + 1} of {total}: {uploaded_file.name}")
            progress_bar.progress((idx) / total)

            saved_path = save_uploaded_image(uploaded_file, uploaded_file.name)
            if saved_path is None:
                st.error(f"Failed to save: {uploaded_file.name}")
                continue

            processed_path = preprocess_image(saved_path)
            ocr_input = processed_path if processed_path else saved_path

            text_lines = extract_text(ocr_input)
            if not text_lines:
                st.warning(f"No text detected in: {uploaded_file.name}")
                entities = {field: "" for field in ENTITY_FIELDS}
            else:
                entities = extract_entities(text_lines)

            entities["_source_file"] = uploaded_file.name
            entities["_raw_text"] = "\n".join(text_lines)
            st.session_state.extracted_data.append(entities)

        progress_bar.progress(1.0)
        status_text.text("Processing complete!")
        st.session_state.processing_done = True
        from src.image_processor import cleanup_processed_images as cleanup
        from src.utils import UPLOAD_DIR
        cleanup(UPLOAD_DIR)

    st.divider()
    st.subheader("📊 Extraction Summary")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.extracted_data)}</div><div class="metric-label">Cards Processed</div></div>', unsafe_allow_html=True)
    with m_col2:
        emails_found = sum(1 for c in st.session_state.extracted_data if c.get("Email"))
        st.markdown(f'<div class="metric-card"><div class="metric-value">{emails_found}</div><div class="metric-label">Emails Found</div></div>', unsafe_allow_html=True)
    with m_col3:
        phones_found = sum(1 for c in st.session_state.extracted_data if c.get("Phone"))
        st.markdown(f'<div class="metric-card"><div class="metric-value">{phones_found}</div><div class="metric-label">Phones Found</div></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📇 Extracted Information")

    for card_idx, card_data in enumerate(st.session_state.extracted_data):
        source_file = card_data.get("_source_file", f"Card {card_idx + 1}")
        raw_text = card_data.get("_raw_text", "")

        with st.expander(f"✨ Card {card_idx + 1}: {source_file}", expanded=(card_idx == 0)):
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
                    with st.popover("🔍 View Raw OCR Text"):
                        st.text(raw_text)

            with col_data:
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                edited_values = {}
                # Group inputs in columns for better density
                i_col1, i_col2 = st.columns(2)
                
                with i_col1:
                    edited_values["Name"] = st.text_input("Name", value=card_data.get("Name", ""), key=f"card_{card_idx}_Name")
                    edited_values["Designation"] = st.text_input("Designation", value=card_data.get("Designation", ""), key=f"card_{card_idx}_Designation")
                    edited_values["Phone"] = st.text_input("Phone", value=card_data.get("Phone", ""), key=f"card_{card_idx}_Phone")
                
                with i_col2:
                    edited_values["Company"] = st.text_input("Company", value=card_data.get("Company", ""), key=f"card_{card_idx}_Company")
                    edited_values["Email"] = st.text_input("Email", value=card_data.get("Email", ""), key=f"card_{card_idx}_Email")
                    edited_values["Website"] = st.text_input("Website", value=card_data.get("Website", ""), key=f"card_{card_idx}_Website")
                
                edited_values["Address"] = st.text_area("Address", value=card_data.get("Address", ""), key=f"card_{card_idx}_Address", height=100)
                
                st.session_state.extracted_data[card_idx].update(edited_values)
                st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    export_data = []
    for card in st.session_state.extracted_data:
        clean_card = {field: card.get(field, "") for field in ENTITY_FIELDS}
        export_data.append(clean_card)

    excel_bytes = export_to_excel_bytes(export_data)
    if excel_bytes:
        st.download_button(
            label="🚀 Download Professional Excel Report",
            data=excel_bytes,
            file_name="business_cards_extracted.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

