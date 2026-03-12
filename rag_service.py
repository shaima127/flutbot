from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.config import config
import os

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None
        self.data_path = "data"

    def process_pdfs(self):
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            return "Data directory was empty, please add PDFs."
        
        loader = DirectoryLoader(self.data_path, glob="./*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        
        if not documents:
            return "No PDFs found in the data directory."

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        self.vector_store.save_local("faiss_index")
        return f"Processed {len(chunks)} chunks from {len(documents)} PDFs."

    def load_index(self):
        if os.path.exists("faiss_index"):
            self.vector_store = FAISS.load_local("faiss_index", self.embeddings, allow_dangerous_deserialization=True)
            return True
        return False

    def retrieve_context(self, query: str, k: int = 3):
        if not self.vector_store:
            if not self.load_index():
                return ""
        
        docs = self.vector_store.similarity_search(query, k=k)
        return "\n".join([doc.page_content for doc in docs])

rag_service = RAGService()
