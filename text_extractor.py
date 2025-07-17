# text_extractor.py

import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from langdetect import detect, LangDetectException
import cv2
import numpy as np
import io

SUPPORTED_IMAGE_TYPES = ['jpg', 'jpeg', 'png']

def is_image_file(filename):
    return any(filename.lower().endswith(ext) for ext in SUPPORTED_IMAGE_TYPES)

def get_first_page_as_image_bytes(file_bytes, filename):
    """Gets the first page of any document as image bytes for visual analysis."""
    if is_image_file(filename):
        return file_bytes
    elif filename.lower().endswith(".pdf"):
        pdf_images = convert_from_bytes(file_bytes, dpi=200, first_page=1, last_page=1)
        if pdf_images:
            img_byte_arr = io.BytesIO()
            pdf_images[0].save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    return None

def preprocess_image(image_bytes):
    """Preprocess image for better OCR accuracy."""
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        # Apply adaptive thresholding for better results on varied lighting
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return Image.fromarray(thresh)
    except Exception:
        return Image.open(io.BytesIO(image_bytes)) # Return original if preprocessing fails

def extract_text(file_bytes: bytes, filename: str):
    """
    Main function: Detects file type and extracts text accordingly.
    Returns: (extracted_text, detected_language)
    """
    full_text = ""
    # Use Tesseract's language packs for Indian languages
    lang_packs = "eng+hin+tam+kan+mal+ben+mar+guj+pan+tel+ori"

    if is_image_file(filename):
        preprocessed_img = preprocess_image(file_bytes)
        full_text = pytesseract.image_to_string(preprocessed_img, lang=lang_packs)
    elif filename.lower().endswith(".pdf"):
        pdf_images = convert_from_bytes(file_bytes, dpi=300)
        for page_img in pdf_images:
            img_byte_arr = io.BytesIO()
            page_img.save(img_byte_arr, format='PNG')
            preprocessed_img = preprocess_image(img_byte_arr.getvalue())
            full_text += pytesseract.image_to_string(preprocessed_img, lang=lang_packs) + "\n\n"
    else:
        raise ValueError("Unsupported file type.")

    try:
        lang = detect(full_text) if full_text.strip() else "en" # Default to English
    except LangDetectException:
        lang = "en" # Default if language detection fails

    return full_text, lang