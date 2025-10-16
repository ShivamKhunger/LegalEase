# This file stores shared constants and mappings to keep the other modules clean.

# Mapping of detected scripts from Tesseract OSD to language codes Tesseract uses.
SCRIPT_TO_LANG_CODE = {
    'Latin': 'eng',
    'Devanagari': 'hin',
    'Bengali': 'ben',
    'Tamil': 'tam',
    'Telugu': 'tel',
    'Kannada': 'kan',
    'Malayalam': 'mal',
    'Gurmukhi': 'pan',
    'Gujarati': 'guj',
    'Oriya': 'ori',
    'Arabic': 'urd',
}

# Mapping from Tesseract language codes to the specific codes required by the mBART translation model.
TESSERACT_TO_MBART = {
    "eng": "en_XX",
    "hin": "hi_IN",
    "ben": "bn_IN",
    "guj": "gu_IN",
    "kan": "kn_IN", 
    "mal": "ml_IN",
    "ori": "or_IN", 
    "pan": "pa_IN", 
    "tam": "ta_IN",
    "tel": "te_IN",
    "urd": "ur_PK"
}

# Language options for the Streamlit UI dropdown.
LANGUAGE_OPTIONS = {
    "Auto-Detect": "auto",
    "English": "eng",
    "Hindi": "hin",
    "Bengali": "ben",
    "Gujarati": "guj",
    "Kannada": "kan",
    "Malayalam": "mal",
    "Oriya": "ori",
    "Punjabi (Gurmukhi)": "pan",
    "Tamil": "tam",
    "Telugu": "tel",
    "Urdu": "urd",
}