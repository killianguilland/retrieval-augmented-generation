import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def ingest_corpus(file_path: str = "corpus/pokemon", index_path: str = "faiss_index"):
    print(f"Loading corpus from {file_path}...")
    loader = DirectoryLoader(file_path, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    documents = loader.load()

    if not documents:
        print(f"No documents found in {file_path}. Please download the corpus first.")
        exit(1)

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Generated {len(chunks)} chunks.")

    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Building FAISS vector store...")
    vectorstore = FAISS.from_documents(chunks, embedding_model)

    print(f"Saving FAISS index to {index_path}...")
    vectorstore.save_local(index_path)
    print("Ingestion complete!")

if __name__ == "__main__":
    if not os.path.exists("corpus/pokemon"):
        print("Error: corpus/pokemon directory not found. Please run wiki_downloader.py first.")
        exit(1)
    
    # Create index directory if it doesn't exist to be safe
    os.makedirs("faiss_index", exist_ok=True)
    
    ingest_corpus()
