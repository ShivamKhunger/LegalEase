# translation.py

from googletrans import Translator, LANGUAGES

# A cache to store translators to avoid re-initializing
_translator_cache = {}

def get_translator():
    """Returns a cached Translator instance."""
    if 'translator' not in _translator_cache:
        _translator_cache['translator'] = Translator()
    return _translator_cache['translator']

def translate_text(text: str, dest_lang: str, src_lang: str = 'auto') -> str:
    """Translates a string of text."""
    if not text or not text.strip() or dest_lang == src_lang:
        return text
    try:
        translator = get_translator()
        translated = translator.translate(text, dest=dest_lang, src=src_lang)
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text # Return original text on failure

def translate_analysis_data(data: dict, dest_lang: str) -> dict:
    """Translates the values of the structured analysis dictionary."""
    if dest_lang == 'en':
        return data

    translated_data = data.copy()
    text_keys = ["summary", "signing_consequences", "signature_locations", "validity_period", "fraud_text_reasoning", "fraud_visual_reasoning"]

    for key in text_keys:
        if key in translated_data and translated_data[key]:
            translated_data[key] = translate_text(translated_data[key], dest_lang)

    if "parties_involved" in translated_data and translated_data["parties_involved"]:
        translated_data["parties_involved"] = [translate_text(p, dest_lang) for p in translated_data["parties_involved"]]

    return translated_data

def get_supported_languages():
    """Returns a dictionary of supported language codes and names."""
    return {code: name.title() for code, name in LANGUAGES.items() if code in ['en', 'hi', 'bn', 'gu', 'kn', 'ml', 'mr', 'pa', 'ta', 'te']}