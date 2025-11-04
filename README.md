# AI Legal Chatbot (India)

LegaBot is a Retrieval-Augmented Generation (RAG) system for Indian legal research. It indexes your PDFs into Pinecone and answers questions using OpenAI with citations from your data.

## Features
- PDF ingestion and chunking (PyMuPDF + LangChain splitters)
- Embeddings via `sentence-transformers/all-MiniLM-L6-v2`
- Pinecone v3 client for vector search
- Two UIs:
  - Chainlit chat (`chainlit run src/ui/app.py`)
  - Streamlit app (`streamlit run src/ui/streamlit_app.py`)

## Project Structure
```
Data/                         # PDFs + generated CSV/NPY
src/
  ingestion/load_pdfs.py      # Extract + clean + chunk PDFs -> Data/legal_text.csv
  embeddings/create_embeddings.py   # Build embeddings -> Data/legal_embeddings.npy
  embeddings/store_pinecone.py      # Upload vectors to Pinecone
  llm/rag_pipeline.py         # Retrieval + LLM answering
  retrieval/search_pinecone.py# CLI Pinecone search
  retrieval/search_query.py   # Local FAISS search (optional)
  ui/app.py                   # Chainlit UI
  ui/streamlit_app.py         # Streamlit UI
```

## Prerequisites
- Python 3.13 (or 3.10+ with compatible wheels)
- Pinecone account and index (dimension 384)
- OpenAI API key

## Setup
1) Clone and create venv
```powershell
cd "D:\AI legal chatbot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies
```powershell
pip install -r requirements.txt
```
If `numpy` or `torch` wheels fail on your Python version, install the suggested compatible versions as prompted by pip, then re-run.

3) Create `.env` in project root
```
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=legal-index
OPENAI_API_KEY=your_openai_key
```

4) Add PDFs to `Data/`

5) Build data artifacts
```powershell
python src/ingestion/load_pdfs.py
python src/embeddings/create_embeddings.py
python src/embeddings/store_pinecone.py
```

## Run the Apps
- Chainlit
```powershell
chainlit run src/ui/app.py -w
```
Then open `http://localhost:8000`.

- Streamlit
```powershell
streamlit run src/ui/streamlit_app.py
```
Then open the URL Streamlit prints (usually `http://localhost:8501`).

## Example Questions
- What is theft under IPC?
- Punishment for murder?
- What section deals with bail?

## Notes
- Ensure your Pinecone index dimension is 384 to match `all-MiniLM-L6-v2`.
- The RAG pipeline queries Pinecone directly and formats source snippets from your data.
- If you change models, recreate embeddings and update the index dimension accordingly.
