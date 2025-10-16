import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import io
import re
from utils import SCRIPT_TO_LANG_CODE

def extract_text_from_document(uploaded_file, language='auto'):
    """
    Extracts text from an uploaded PDF or image file using OCR.
    Handles script detection and provides status updates via Streamlit.
    """
    # NOTE: The hardcoded path to tesseract.exe has been REMOVED.
    # The system will now find it automatically on both local and deployed environments.

    if uploaded_file is None:
        return "", "eng"

    file_extension = uploaded_file.name.split('.')[-1].lower()
    file_bytes = uploaded_file.getvalue()
    images = []

    try:
        if file_extension == 'pdf':
            images.extend(convert_from_bytes(file_bytes))
        elif file_extension in ['png', 'jpg', 'jpeg', 'bmp', 'tiff']:
            images.append(Image.open(io.BytesIO(file_bytes)))
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return "", "eng"
    except Exception as img_err:
        st.error(f"Could not read or process the file. Error: {img_err}")
        return "", "eng"

    if not images:
        st.error("Could not convert the document to images for processing.")
        return "", "eng"

    final_lang_code = language
    if language == 'auto':
        try:
            osd_data = pytesseract.image_to_osd(images[0])
            script_match = re.search(r'Script: ([^\n]+)', osd_data)
            if script_match:
                detected_script = script_match.group(1).strip()
                final_lang_code = SCRIPT_TO_LANG_CODE.get(detected_script, 'eng')
                st.sidebar.success(f"Detected: {detected_script} | Using: {final_lang_code.upper()}")
            else:
                st.sidebar.warning("Could not determine script. Defaulting to English.")
                final_lang_code = 'eng'
        except Exception as osd_error:
            st.sidebar.error(f"Script detection failed. Defaulting to English.")
            final_lang_code = 'eng'
    
    extracted_text = ""
    try:
        for image in images:
            extracted_text += pytesseract.image_to_string(image, lang=final_lang_code) + "\n\n"
        return extracted_text, final_lang_code
    except Exception as e:
        st.error(f"Text extraction failed. Ensure the Tesseract language pack ('{final_lang_code}') is installed.")
        st.error(f"See setup guide for details. Error: {e}")
        return "", final_lang_code
