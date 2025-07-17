import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

import text_extractor
import translation
import analysis_engine
import qna

st.set_page_config(layout="wide", page_title="LegalEase", page_icon="⚖️")

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

with st.sidebar:
    st.header("Configuration")
    api_key_input = st.text_input("Enter your Google AI API Key", type="password", value=GOOGLE_API_KEY)
    
    if api_key_input:
        try:
            genai.configure(api_key=api_key_input)
            st.success("API Key configured successfully!")
        except Exception as e:
            st.error(f"Failed to configure API Key: {e}")
    else:
        st.warning("Please enter your Google AI API Key to begin.")

st.title("⚖️ LegalEase: AI-Powered Legal Document Analysis")
st.markdown("Upload a legal document (PDF, JPG, PNG) to get a simplified summary, risk analysis, and ask questions in your preferred language.")

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

uploaded_file = st.file_uploader("Upload your document", type=["pdf", "jpg", "png", "jpeg"])

if uploaded_file and api_key_input:
    if st.session_state.analysis_results is None:
        with st.spinner("Analyzing document... This may take a few moments..."):
            file_bytes = uploaded_file.getvalue()
            filename = uploaded_file.name

            raw_text, src_lang = text_extractor.extract_text(file_bytes, filename)
            
            english_text = translation.translate_text(raw_text, dest_lang='en', src_lang=src_lang)
            
            text_analysis = analysis_engine.get_structured_analysis(english_text)
            first_page_bytes = text_extractor.get_first_page_as_image_bytes(file_bytes, filename)
            visual_analysis = analysis_engine.get_visual_fraud_score(first_page_bytes)
            
            final_fraud_score = (text_analysis.get('fraud_text_score', 0) + visual_analysis.get('fraud_visual_score', 0)) / 2
            
            vector_store = qna.create_vector_store(english_text, api_key_input)
            st.session_state.qa_chain = qna.create_qa_chain(vector_store, api_key_input) if vector_store else None
            
            st.session_state.analysis_results = {
                "english_analysis": {**text_analysis, **visual_analysis},
                "final_fraud_score": final_fraud_score
            }

if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    supported_langs = translation.get_supported_languages()
    lang_code = st.selectbox("View analysis in:", options=supported_langs.keys(), format_func=lambda code: supported_langs[code])

    display_analysis = translation.translate_analysis_data(results["english_analysis"], lang_code)
    
    fraud_score = results["final_fraud_score"]
    if fraud_score > 65:
        st.error(f"🚨 **High Fraud Risk Detected** (Confidence: {fraud_score:.0f}%)")
        with st.expander("See Fraud Analysis Details"):
            st.write(f"**Text-based Analysis:** {display_analysis.get('fraud_text_reasoning', 'N/A')}")
            st.write(f"**Visual Analysis:** {display_analysis.get('fraud_visual_reasoning', 'N/A')}")
    
    st.subheader("Document Overview")
    col1, col2 = st.columns(2)
    with col1:
        parties_list = display_analysis.get('parties_involved', ['Not found'])
        formatted_parties = "- " + "\n- ".join(parties_list)
        st.info(f"**Parties Involved:**\n\n{formatted_parties}")
    with col2:
        st.warning(f"**Agreement Validity:** {display_analysis.get('validity_period', 'Not found')}")
    
    with st.expander("📄 Document Summary", expanded=True):
        st.write(display_analysis.get('summary', 'Summary not available.'))
    
    with st.expander("✍️ Consequences & Signature Locations"):
        st.write("**Upon Signing:**", display_analysis.get('signing_consequences', 'Not found'))
        st.write("**Signature Locations:**", display_analysis.get('signature_locations', 'Not found'))

    st.subheader("❓ Ask a Question About the Document")
    
    if st.session_state.qa_chain is None:
        st.warning("Q&A is unavailable for this document (could not process text).")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("e.g., What is the penalty for late payment?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("Thinking..."):
                english_prompt = translation.translate_text(prompt, dest_lang='en')
                english_response = qna.get_rag_response(st.session_state.qa_chain, english_prompt, st.session_state.chat_history)
                final_response = translation.translate_text(english_response, dest_lang=lang_code)

            st.session_state.chat_history.append({"role": "AI", "content": final_response})
            with st.chat_message("AI"):
                st.markdown(final_response)

if not uploaded_file and not api_key_input:
    st.info("Enter your API key in the sidebar and upload a document to get started.")