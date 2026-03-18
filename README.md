# Système RAG - TP ESIEE Paris

Ce projet implémente un système RAG (Retrieval Augmented Generation) tel que demandé par le TP.

Au lieu de demander à un LLM de répondre uniquement à partir de ce qu'il "sait", on lui fournit des extraits pertinents d'un corpus de documents. Le LLM génère alors sa réponse en s'appuyant sur ces extraits.

## Prérequis

- Python 3.10+
- `pipenv`

## Installation

Ce projet utilise [Pipenv](https://pipenv.pypa.io/en/latest/) pour la gestion des dépendances.

1. **Cloner le repository** et se placer à la racine :
   ```bash
   git clone <url-du-repo>
   cd retrieval-augmented-generation
   ```

2. **Installer les dépendances** :
   ```bash
   pipenv install
   ```

3. **Configurer les clés API** :
   Copiez le fichier d'exemple et renommez-le `.env` :
   ```bash
   cp .env.template .env
   ```
   **Important** : Ouvrez le fichier `.env` et remplacez par votre propre clé `OPENROUTER_API_KEY`.

## Utilisation Détaillée

### 1. Télécharger un corpus depuis un wiki (Optionnel)
Ce projet intègre le script `wiki_downloader.py`, un outil permettant d'extraire le texte brut d'articles provenant de n'importe quel site propulsé par MediaWiki.
L'exemple par défaut télécharge une sélection d'articles Pokémon de la Génération 1 dans le dossier `corpus/pokemon` :
```bash
pipenv run python wiki_downloader.py bulk Bulbasaur Charmander Squirtle Pikachu Eevee Mewtwo Mew Gengar Snorlax Dragonite "Pallet Town" "Indigo Plateau" "Kanto" "Professor Oak" "Pokémon Red and Blue" --dir corpus/pokemon
```
> *Vous pouvez modifier les URL dans le script pour pointer vers n'importe quel autre Wiki (Memory Alpha, Tolkien Gateway, etc).*
> *Commandes additionnelles :* `search "query"` *ou* `category "Category Name"`

### 2. Ingérer les données (Vectorisation FAISS)
Une fois votre corpus téléchargé, il faut l'indexer pour que le LLM puisse le parcourir :
```bash
pipenv run python src/ingest.py
```
*Note : Le script `src/ingest.py` parcourt automatiquement les fichiers `.txt` du répertoire `corpus/pokemon`, les tronçonne (chunking), calcule leurs embeddings, et sauvegarde la base de données vectorielle résultante dans le dossier `faiss_index/`.*

### 3. Lancer l'interface Web RAG (Streamlit)
Dès lors que l'ingestion est terminée (`faiss_index/` présent), vous pouvez interagir avec l'interface graphique :
```bash
pipenv run streamlit run app.py
```
Rendez-vous sur l'URL locale affichée dans la console (généralement `http://localhost:8501`) pour poser vos questions à l'agent RAG !

### 4. Mode CLI (Diagnostic rapide)
Il est aussi possible de tester une recherche complète en invite de commandes :
```bash
pipenv run python src/rag.py
```

## Stack Technique
- **LangChain**, **FAISS**, **Sentence-Transformers** (`all-MiniLM-L6-v2`)
- **Reranking** avec CrossEncoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) intégré pour affiner les chunks retenus.
- **OpenRouter** pour l'inférence LLM (Mistral-7b).
- **Streamlit** pour la web app.

