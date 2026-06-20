import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from shared.logger import get_logger

logger = get_logger(__name__)


# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIRECTORY = os.path.join(BASE_DIR, "data", "pdfs")
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# Create directories if they don't exist
os.makedirs(PDF_DIRECTORY, exist_ok=True)
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

def load_documents(directory):
    """Reads all PDFs from the specified directory."""
    documents = []
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            full_path = os.path.join(directory, file)
            loader = PyPDFLoader(full_path)
            documents.extend(loader.load())
            logger.info("Loaded document", extra={"extra": {"file": file}})
    return documents

def process_texts(documents):
    """Splits documents into smaller chunks with overlap."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info("Documents split into chunks", extra={"extra": {"chunk_count": len(chunks)}})
    return chunks

def create_or_update_vector_store():
    """Full pipeline: loads, splits, generates embeddings and saves to ChromaDB."""
    logger.info("Starting Knowledge Base construction...")
    
    # 1. Load
    documents = load_documents(PDF_DIRECTORY)
    if not documents:
        logger.warning("No PDFs found. Place files in the /data/pdfs folder.", extra={"extra": {"directory": PDF_DIRECTORY}})
        return None

    # 2. Process (Chunking)
    chunks = process_texts(documents)

    # 3. Embeddings (Using local, lightweight HuggingFace model)
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Save to Chroma (persisting to disk)
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings_model,
        persist_directory=CHROMA_PERSIST_DIR
    )
    logger.info("Knowledge Base saved successfully", extra={"extra": {"persist_directory": CHROMA_PERSIST_DIR}})
    
    return vector_store

def test_search(query):
    """Function to test if the RAG is returning the correct data."""
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Loads the existing database from disk
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR, 
        embedding_function=embeddings_model
    )
    
    # Configures the Retriever (fetches the 3 most relevant chunks)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    results = retriever.invoke(query)
    
    logger.info("Searching", extra={"extra": {"query": query}})
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', 'N/A')
        logger.info("Search result", extra={"extra": {
            "result_index": i, 
            "source": source, 
            "page": page,
            "content": doc.page_content
        }})
        

# ==========================================
# Script Execution
# ==========================================
if __name__ == "__main__":
    # Step 1: Build the base (Run this only when adding new PDFs)
    #create_or_update_vector_store()
    
    # Step 2: Test a search (Uncomment after creating the base)
    test_search("Qual a taxa de empréstimo consignado?")
