import streamlit as st
import os
import sys

# Add current dir to python path to import src modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag import rag_pipeline

st.set_page_config(page_title="Système RAG - ESIEE Paris", page_icon="🤖")

st.title("Système RAG 🤖📚")

st.markdown("""
Bienvenue dans le TP de test RAG.
Posez une question sur le corpus ingéré (ex: *Que représente la flamme de Charmander / Salamèche ?*)
""")

question = st.text_input("Votre question :")

if st.button("Rechercher"):
    if question:
        if not os.path.exists("faiss_index"):
            st.error("L'index FAISS n'a pas été trouvé. Veuillez d'abord exécuter `pipenv run python src/ingest.py`.")
        elif not os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY") == "sk-or-v1-your-key-here":
             st.warning("Précisez votre OPENROUTER_API_KEY dans le fichier .env.")
        else:
            with st.spinner("Recherche et génération en cours ..."):
                try:
                    answer, chunks = rag_pipeline(question)
                    
                    st.subheader("Réponse")
                    st.info(answer)
                    
                    st.subheader("Sources (Chunks)")
                    for i, chunk in enumerate(chunks, 1):
                        with st.expander(f"Source {i}"):
                            st.write(chunk)
                except Exception as e:
                    st.error(f"Une erreur est survenue: {e}")
    else:
        st.warning("Veuillez entrer une question.")
