import google.generativeai as genai
from PIL import Image
import json
import io

def get_model(model_name='gemini-1.5-flash'):
    """Initializes and returns a GenerativeModel."""
    return genai.GenerativeModel(model_name)

def get_structured_analysis(text: str) -> dict:
    """
    Analyzes text to extract key legal information and a text-based fraud score.
    Returns a dictionary.
    """
    model = get_model()
    prompt = f"""
    Analyze the following legal document text. Your response MUST be a single, valid JSON object.
    Do not include any text or markdown formatting before or after the JSON.
    Extract the following fields:
    - "summary": A brief, simple summary of the document's purpose.
    - "parties_involved": A list of strings, with each string identifying a party (e.g., 'Landlord: John Doe').
    - "signing_consequences": A clear, concise explanation of the primary consequences of signing.
    - "signature_locations": A text description of where signatures are required.
    - "validity_period": The start and end dates or duration of the agreement.
    - "fraud_text_score": An integer score from 0 (safe) to 100 (highly suspicious) based on suspicious, predatory, or unusual clauses in the text.
    - "fraud_text_reasoning": A brief string explaining the reasoning for the text fraud score.

    If a field cannot be found, return a null value for it.

    Document Text:
    ---
    {text}
    ---
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error during structured analysis: {e}")
        return {"error": str(e)}

def get_visual_fraud_score(image_bytes: bytes) -> dict:
    """
    Uses a multi-modal model to analyze a document image for signs of forgery.
    """
    if not image_bytes:
        return {"fraud_visual_score": 0, "fraud_visual_reasoning": "No image provided for visual analysis."}

    model = get_model()
    image = Image.open(io.BytesIO(image_bytes))

    prompt = """
    You are a forensic document examiner. Analyze this image of a legal document page.
    Your response MUST be a single, valid JSON object.
    Look for visual signs of forgery: distorted seals/emblems, pixelated signatures, inconsistent fonts, or misaligned text.
    Provide:
    - "fraud_visual_score": An integer from 0 (looks authentic) to 100 (likely forged).
    - "fraud_visual_reasoning": A brief string explaining your reasoning.
    """
    try:
        response = model.generate_content([prompt, image])
        cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error during visual analysis: {e}")
        return {"error": str(e)}