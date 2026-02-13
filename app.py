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

if st.session_state.processing_done and st.session_state.extracted_data:
    st.divider()
    st.subheader("Extracted Information")

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
                    with st.popover("View Raw OCR Text"):
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

    export_data = []
    for card in st.session_state.extracted_data:
        clean_card = {field: card.get(field, "") for field in ENTITY_FIELDS}
        export_data.append(clean_card)

    excel_bytes = export_to_excel_bytes(export_data)
    if excel_bytes:
        st.download_button(
            label="Download Excel Report",
            data=excel_bytes,
            file_name="business_cards_extracted.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

    st.divider()
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cards Processed", len(st.session_state.extracted_data))
    with col2:
        emails_found = sum(1 for c in st.session_state.extracted_data if c.get("Email"))
        st.metric("Emails Found", emails_found)
    with col3:
        phones_found = sum(1 for c in st.session_state.extracted_data if c.get("Phone"))
        st.metric("Phones Found", phones_found)
