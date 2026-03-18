import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def retrieve_chunks(question, index_path="faiss_index", k=3):
    """
    Retrieve top-k relevant chunks from FAISS vector store.
    Utilise le reranking avec CrossEncoder.
    """
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Missing FAISS index at {index_path}. Please run src/ingest.py first.")
    
    vectorstore = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)
    
    # Retrieval initial de 10 chunks (plus que k final)
    docs = vectorstore.similarity_search(question, k=10)
    chunks = [doc.page_content for doc in docs]
    
    # Reranking
    try:
        from sentence_transformers import CrossEncoder
        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [[question, chunk] for chunk in chunks]
        scores = reranker.predict(pairs)
        
        # Tri des chunks par score décroissant
        scored_chunks = list(zip(scores, chunks))
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        return [chunk for score, chunk in scored_chunks[:k]]
    except Exception as e:
        print(f"Warning: Reranking failed ({e}). Falling back to base retrieval.")
        return chunks[:k]

def generate_answer(question, chunks):
    """
    Generate an answer using the OpenRouter LLM based on retrieved chunks.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "sk-or-v1-your-key-here":
        return "Veuillez configurer votre clé OPENROUTER_API_KEY dans le fichier .env."

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    context = "\n\n---\n\n".join(chunks)
    
    prompt = f"""Réponds à la question

{question}

avec les informations suivantes:

{context}

Tu es un expert dans ce domaine. Réponds de manière concise, précise, et utile, en format markdown."""

    try:
        response = client.chat.completions.create(
            # Using a free model as suggested by the TP subject
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de l'appel à l'API OpenRouter: {e}"

def rag_pipeline(question):
    """
    Full pipeline: Given a question, retrieve chunks, and generate answer.
    """
    chunks = retrieve_chunks(question)
    answer = generate_answer(question, chunks)
    return answer, chunks

if __name__ == "__main__":
    q = "Que représente la flamme sur la queue de Salamèche ?"
    ans, chnks = rag_pipeline(q)
    print("--- Question ---")
    print(q)
    print("\n--- Réponse ---")
    print(ans)
    print("\n--- Sources ---")
    for i, c in enumerate(chnks):
        print(f"[{i+1}] {c}")
