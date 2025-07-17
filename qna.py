from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

def create_vector_store(text: str, api_key: str):
    """Creates a FAISS vector store from the document text."""
    if not text.strip():
        return None
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        if not chunks:
            return None
        vector_store = FAISS.from_texts(texts=chunks, embedding=embeddings)
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None

def create_qa_chain(vector_store, api_key: str):
    """Creates a conversational retrieval chain."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.3)
    retriever = vector_store.as_retriever()

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given a chat history and the latest user question, formulate a standalone question that can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
        ("human", "{chat_history}\n\n{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant for answering questions about a legal document. Answer the user's question based on the context provided below. Be concise and clear. If the context doesn't contain the answer, say that you cannot find the information in the document.\n\nContext:\n{context}"),
        ("human", "{chat_history}\n\nQuestion: {input}"),
    ])
    Youtube_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, Youtube_chain)
    return rag_chain

def get_rag_response(chain, question: str, chat_history: list):
    """Gets an answer from the RAG chain."""
    history_messages = [AIMessage(content=msg["content"]) if msg["role"] == "AI" else HumanMessage(content=msg["content"]) for msg in chat_history]
    response = chain.invoke({"input": question, "chat_history": history_messages})
    return response['answer']