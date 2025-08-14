import os
import pdfplumber # type: ignore
from werkzeug.utils import secure_filename # type: ignore
from langchain_groq import ChatGroq # type: ignore
from langchain_core.prompts import PromptTemplate# type: ignore 
from langchain.chains import RetrievalQA # type: ignore
from langchain_community.vectorstores.faiss import FAISS # type: ignore
from langchain_huggingface import HuggingFaceEmbeddings # type: ignore
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

# groq_api_key = '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'
groq_api_key = os.getenv("GROQ_API_KEY")
print("Loaded GROQ_API_KEY:", groq_api_key)
# os.environ["OLLAMA_API_KEY"] = "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"
ollama_api_key = os.getenv("OLLAMA_API_KEY")
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile", max_tokens=32768)


# Step 2: Build the RAG pipeline
# def build_rag_pipeline(vector_store):
#     retriever = vector_store.as_retriever()
#     # llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile", max_tokens=32768)

#     return RetrievalQA(llm=llm, retriever=retriever)
def build_rag_pipeline(vector_store):
    """
    Build a Retrieval-Augmented Generation (RAG) pipeline.
    Args:
        vector_store: The FAISS vector store.
    Returns:
        A RetrievalQA chain.
    """
    retriever = vector_store.as_retriever()

    # Define a prompt template for the QA chain
    prompt_template = """
    Use the following document to answer the question. If the question asks for a summary or bullet points, format the response using markdown with proper bullet points (using - or *). Make sure each point is on a new line:

    Context:
    {context}
    
    Question: {question}
    
    Answer (use markdown formatting if summarizing):"""
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template,
    )

    # Wrap ChatGroq with the prompt
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Or use "map_reduce" or "refine" if applicable
        retriever=retriever,
        return_source_documents=True,  # Include documents in the response if needed
        chain_type_kwargs={"prompt": prompt},
    )

# Extract text from the uploaded PDF
def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if not text.strip():
            return "No extractable text found in the PDF."
        return text
    except Exception as e:
        return f"Error during PDF extraction: {str(e)}"



def create_vector_store(text):
    """
    Create a FAISS vector store from the provided text using Llama embeddings.
    Args:
        text (str): Input text for embeddings.
    Returns:
        FAISS: FAISS vector store.
    """

    # # embeddings = OllamaEmbeddings()  # Use Llama embeddings
    # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # vector_store = FAISS.from_texts([text], embedding=embeddings)
    # return vector_store

    if not text.strip():
        raise ValueError("Cannot create a vector store with empty text.")
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = FAISS.from_texts([text], embedding=embeddings)
        return vector_store
    except Exception as e:
        raise RuntimeError(f"Error creating vector store: {e}")



def generate_response(question, pdf_text=None):
    """
    Generate a response to a user query with or without PDF context.
    Args:
        question (str): The user's question.
        pdf_text (str, optional): Text extracted from an uploaded PDF. Defaults to None.
    Returns:
        str: Response from the model.
    """
    try:
        if pdf_text:
            if os.path.exists(pdf_text):
                pdf_text = extract_text_from_pdf(pdf_text)
            # Use RAG pipeline with the PDF context
            vector_store = create_vector_store(pdf_text)
            rag_pipeline = build_rag_pipeline(vector_store)
            response = rag_pipeline.invoke({"query": question})  # Ensure this function works with your RAG pipeline

            
        else:
            # Use LLM directly without PDF context for general questions
            # llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile", max_tokens=32768)

            messages = [{"role": "user", "content": question}]

            # Directly pass the question string as a prompt (simpler method)
            response = llm.invoke(question)  # Just passing the question directly as a string
        
            
        return response
    except Exception as e:
        return f"Error generating response: {e}"
