import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from shared.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIRECTORY = os.path.join(BASE_DIR, "data", "pdfs")
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

os.makedirs(PDF_DIRECTORY, exist_ok=True)
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

def _load_documents(directory):
    """Reads all PDFs from the specified directory."""
    documents = []
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            full_path = os.path.join(directory, file)
            loader = PyPDFLoader(full_path)
            documents.extend(loader.load())
            logger.info("Loaded document", extra={"extra": {"file": file}})
    return documents

def _process_texts(documents):
    """Splits documents into smaller chunks with overlap."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info("Documents split into chunks", extra={"extra": {"chunk_count": len(chunks)}})
    return chunks

def _create_vector_store():
    """Full pipeline: loads, splits, generates embeddings and saves to ChromaDB."""
    logger.info("Starting Knowledge Base construction...")
    
    documents = _load_documents(PDF_DIRECTORY)
    if not documents:
        logger.warning("No PDFs found. Place files in the /data/pdfs folder.", extra={"extra": {"directory": PDF_DIRECTORY}})
        return None

    chunks = _process_texts(documents)

    embeddings_model = HuggingFaceEmbeddings(model_name=os.getenv("EMBED_MODEL"))

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings_model,
        persist_directory=CHROMA_PERSIST_DIR
    )
    logger.info("Knowledge Base saved successfully", extra={"extra": {"persist_directory": CHROMA_PERSIST_DIR}})
    
    return vector_store

def search(query: str) -> str:
    """Busca informações na base de conhecimento sobre regras, taxas e processos do banco."""
    embeddings_model = HuggingFaceEmbeddings(model_name=os.getenv("EMBED_MODEL"))
    
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR, 
        embedding_function=embeddings_model
    )
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    results = retriever.invoke(query)
    
    logger.info("Searching", extra={"extra": {"query": query}})
    
    if not results:
        return "Nenhuma informação encontrada na base de conhecimento."
        
    final_answer = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown')

        if source != 'Unknown':
            source = os.path.basename(source)

        page = doc.metadata.get('page', 'N/A')
        logger.info("Search result", extra={"extra": {
            "result_index": i, 
            "source": source, 
            "page": page,
            "content": doc.page_content
        }})
        final_answer.append(f"[Fonte: {source}, Página: {page}]\n{doc.page_content}")
    
    return "\n\n".join(final_answer)
        

if __name__ == "__main__":
    #_create_vector_store()
    #search("Qual a taxa de empréstimo consignado?")
    pass
