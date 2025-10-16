import streamlit as st
import groq
import json

# --- AI Functionality (Prepared for Deployment) ---

def get_translation(groq_api_key):
    with st.spinner("Translating..."):
        try:
            client = groq.Groq(api_key=groq_api_key)
            source_language = st.session_state.get('source_lang_code', 'hin')
            prompt = f"Translate the following text from {source_language} to English. Provide only the translated text, without any introduction.\n\nTEXT:\n---\n{st.session_state.extracted_text}\n---\n\nTRANSLATION:"
            chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.1-8b-instant")
            st.session_state.translated_text = chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Translation failed via API. Error: {e}")

def get_summary(groq_api_key):
    with st.spinner("Summarizing..."):
        try:
            client = groq.Groq(api_key=groq_api_key)
            text_to_summarize = st.session_state.get('translated_text', st.session_state.extracted_text)
            prompt = f"Summarize the following legal document text concisely. Focus on key points and obligations. Provide the summary in a single paragraph.\n\nDOCUMENT TEXT:\n---\n{text_to_summarize}\n---\n\nSUMMARY:"
            chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.1-8b-instant")
            st.session_state.summary = chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Summarization failed via API. Error: {e}")

def get_qa_answer(groq_api_key, question):
    client = groq.Groq(api_key=groq_api_key)
    context = st.session_state.get('translated_text', st.session_state.get('extracted_text', ''))
    if not context.strip():
        st.error("Document text is empty."); return
    try:
        with st.spinner("Analyzing document..."):
            gatekeeper_prompt = f"""Based *only* on the DOCUMENT TEXT below, can the user's question be answered? Respond with a single JSON object with one key, "answer_in_document", which is either true or false. DOCUMENT TEXT: --- {context} --- USER'S QUESTION: "{question}" JSON RESPONSE:"""
            gatekeeper_completion = client.chat.completions.create(messages=[{"role": "user", "content": gatekeeper_prompt}], model="llama-3.1-8b-instant", temperature=0, response_format={"type": "json_object"})
            is_answer_in_doc = json.loads(gatekeeper_completion.choices[0].message.content).get("answer_in_document", False)
        if is_answer_in_doc:
            with st.spinner("Generating response from document..."):
                answer_prompt = f"""You are an expert legal assistant. Answer the user's question based *only* on the provided DOCUMENT TEXT. Explain any complex legal terms using your own knowledge, but ground the core answer in the document. DOCUMENT TEXT: --- {context} --- USER'S QUESTION: "{question}" ANSWER:"""
                final_completion = client.chat.completions.create(messages=[{"role": "user", "content": answer_prompt}], model="llama-3.1-8b-instant")
                st.session_state.qa_answer = final_completion.choices[0].message.content
        else:
            with st.spinner("Consulting knowledge base..."):
                answer_prompt = f"""You are a helpful research assistant. You could not find the answer to the user's question in their document. Answer the user's question based on your own extensive general knowledge. USER'S QUESTION: "{question}" ANSWER:"""
                final_completion = client.chat.completions.create(messages=[{"role": "user", "content": answer_prompt}], model="llama-3.1-8b-instant")
                st.session_state.qa_answer = "I could not find a direct answer in your document. However, based on my general knowledge, here is an explanation:\n\n" + final_completion.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred with the Q&A model: {e}")

def analyze_document_authenticity(groq_api_key, document_text):
    try:
        client = groq.Groq(api_key=groq_api_key)
        prompt = f"""You are a forensic document analysis AI. Assess the likelihood that the provided text is from a fake or fraudulent document. Analyze for red flags like poor grammar, urgency, missing info, or vague terms. Respond with a single JSON object with two keys: "is_fake_confidence_score": an integer (0-100), and "reasoning": a brief, one-sentence explanation. DOCUMENT TEXT: --- {document_text} --- JSON RESPONSE:"""
        analysis_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.1-8b-instant", temperature=0, response_format={"type": "json_object"})
        result = json.loads(analysis_completion.choices[0].message.content)
        return result.get("is_fake_confidence_score", 0), result.get("reasoning", "No specific reason provided.")
    except Exception as e:
        st.error(f"Document authenticity analysis failed: {e}")
        return 0, "Analysis could not be completed."