import streamlit as st
import pandas as pd
from io import BytesIO
import re
from PIL import Image
import tempfile
import os

# Page config
st.set_page_config(
    page_title="Business Card Intelligence",
    page_icon="📇",
    layout="wide"
)

# CSS
st.markdown("""
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
.stButton>button {
    background-color: #2F5496;
    color: white;
    border-radius: 6px;
    padding: 0.5rem 2rem;
}
.demo-notice {
    background: #e8f5e8;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    border: 1px solid #c3e6c3;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📇 Business Card Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload business card images to extract contact information</div>', unsafe_allow_html=True)

# Demo notice
st.markdown("""
<div class="demo-notice">
ℹ️ <strong>Demo Mode:</strong> This is a demonstration version. Upload images to see how the interface works with sample OCR results.
</div>
""", unsafe_allow_html=True)

# Session state
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = []

# File upload
uploaded_files = st.file_uploader(
    "Upload business card images",
    type=['jpg', 'jpeg', 'png', 'webp'],
    accept_multiple_files=True,
    help="Supported formats: JPG, PNG, WebP"
)

if uploaded_files:
    if st.button("🔍 Extract Information", type="primary", use_container_width=True):
        st.session_state.extracted_data = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Sample data for demo
        sample_contacts = [
            {
                "Name": "John Doe",
                "Title": "Software Engineer", 
                "Company": "Tech Company Inc.",
                "Email": "john.doe@techcompany.com",
                "Phone": "(555) 123-4567",
                "Address": "123 Tech Street, Silicon Valley, CA 94000",
                "Website": "www.techcompany.com"
            },
            {
                "Name": "Jane Smith",
                "Title": "Marketing Director",
                "Company": "Creative Agency", 
                "Email": "jane.smith@creative.com",
                "Phone": "(555) 987-6543",
                "Address": "456 Design Ave, New York, NY 10001",
                "Website": "www.creative.com"
            },
            {
                "Name": "Robert Johnson",
                "Title": "CEO",
                "Company": "Startup Ventures",
                "Email": "robert.j@startup.io", 
                "Phone": "(555) 246-8135",
                "Address": "789 Innovation Blvd, Austin, TX 73301",
                "Website": "www.startup.io"
            }
        ]
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing card {idx + 1} of {len(uploaded_files)}: {uploaded_file.name}")
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
            # Use sample data
            sample_data = sample_contacts[idx % len(sample_contacts)].copy()
            sample_data["_source_file"] = uploaded_file.name
            sample_data["_raw_text"] = f"""{sample_data['Name']}
{sample_data['Title']}
{sample_data['Company']}
{sample_data['Email']}
{sample_data['Phone']}
{sample_data['Address']}
{sample_data['Website']}"""
            
            st.session_state.extracted_data.append(sample_data)
        
        progress_bar.progress(1.0)
        status_text.text("Processing complete!")
        st.success(f"Successfully processed {len(uploaded_files)} business card(s)!")

# Display results
if st.session_state.extracted_data:
    st.divider()
    st.subheader("📋 Extracted Information")
    
    for card_idx, card_data in enumerate(st.session_state.extracted_data):
        source_file = card_data.get("_source_file", f"Card {card_idx + 1}")
        
        with st.expander(f"Card {card_idx + 1}: {source_file}", expanded=True):
            col_img, col_data = st.columns([1, 2])
            
            with col_img:
                if uploaded_files:
                    for uf in uploaded_files:
                        if uf.name == source_file:
                            st.image(uf, caption=source_file, use_container_width=True)
                            break
            
            with col_data:
                fields = ["Name", "Title", "Company", "Email", "Phone", "Address", "Website"]
                for field in fields:
                    value = st.text_input(
                        field,
                        value=card_data.get(field, ""),
                        key=f"card_{card_idx}_{field}"
                    )
                    card_data[field] = value
                
                # Raw text toggle
                if st.button("👁️ View Raw OCR Text", key=f"raw_{card_idx}"):
                    st.text_area("Extracted Text", card_data.get("_raw_text", ""), height=150)
    
    st.divider()
    
    # Export functionality
    export_data = []
    for card in st.session_state.extracted_data:
        clean_card = {field: card.get(field, "") for field in ["Name", "Title", "Company", "Email", "Phone", "Address", "Website"]}
        export_data.append(clean_card)
    
    df = pd.DataFrame(export_data)
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Business Cards')
    excel_buffer.seek(0)
    
    st.download_button(
        label="📊 Download Excel Report",
        data=excel_buffer.getvalue(),
        file_name="business_cards_extracted.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
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

# Instructions
if not st.session_state.extracted_data:
    st.info("👆 Upload business card images above to see the OCR extraction process in action!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
<p><strong>Business Card Intelligence</strong> - Demo Version</p>
<p>This is a demonstration of the business card OCR application.</p>
</div>
""", unsafe_allow_html=True)
