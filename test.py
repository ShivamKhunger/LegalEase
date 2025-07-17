# app.py

import streamlit as st
from core.text_extractor import extract_text

st.set_page_config(page_title="LegalEase AI", layout="wide")
st.title("📄 LegalEase AI - Legal Document Analyzer")

# --- Sidebar for future features ---
with st.sidebar:
    st.header("🔧 Options")
    st.info("Upload any legal document (PDF or image).\nIt will auto-detect language & extract text.")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload PDF, JPG, PNG", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = uploaded_file.read()

    with st.spinner("🔍 Extracting text using OCR..."):
        try:
            text, lang_code, meta = extract_text(file_bytes, uploaded_file.name)
        except Exception as e:
            st.error(f"❌ Error while processing file: {e}")
            st.stop()

    st.success(f"✅ Extracted from {meta['type'].upper()} | Pages: {meta['pages']} | Language: `{lang_code.upper()}`")

    st.text_area("📝 Extracted Text (Editable)", value=text, height=400)

    # Save for downstream (summary, translation, chat, etc.)
    st.session_state["raw_text"] = text
    st.session_state["lang_code"] = lang_code
    st.session_state["file_meta"] = meta

else:
    st.warning("⬆ Please upload a file to get started.")
