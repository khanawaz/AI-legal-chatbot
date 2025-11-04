import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict

import numpy as np
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1️⃣ Load environment variables
project_root = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=project_root / ".env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT") or os.getenv("PINECONE_ENV")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

missing_env = [
    name for name, val in [
        ("PINECONE_API_KEY", PINECONE_API_KEY),
        ("PINECONE_ENVIRONMENT", PINECONE_ENV),
        ("PINECONE_INDEX_NAME", INDEX_NAME),
        ("OPENAI_API_KEY", OPENAI_API_KEY),
    ]
    if not val
]
if missing_env:
    raise RuntimeError(
        "Missing required environment variables: " + ", ".join(missing_env) +
        ". Please add them to your .env at project root."
    )

# 2️⃣ Initialize Pinecone (v3 client)
pc = Pinecone(api_key=PINECONE_API_KEY)
try:
    index = pc.Index(INDEX_NAME)
except Exception as e:
    raise RuntimeError(
        f"Failed to connect to Pinecone index '{INDEX_NAME}'. Ensure it exists and API key/env are correct. Error: {e}"
    )

# 3️⃣ Create embedding model for queries
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_query(text: str) -> List[float]:
    vec = embedding_model.encode([text], normalize_embeddings=True)
    return vec.astype(np.float32)[0].tolist()

def retrieve_context(query: str, top_k: int = 5) -> List[Dict]:
    query_vec = embed_query(query)
    results = index.query(vector=query_vec, top_k=top_k, include_metadata=True)
    matches = results.get("matches", []) or []
    return matches

# 4️⃣ Define system prompt
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are LegaBot, an Indian legal research assistant.\n"
        "Use only the provided context to answer questions clearly and concisely.\n"
        "Always cite the IPC/CrPC section number or case name.\n"
        "If unsure, say you are not certain and recommend consulting a lawyer.\n\n"
        "📚 Context:\n{context}\n\n"
        "❓ Question:\n{question}\n\n"
        "🧾 Answer:"
    )
)

# 5️⃣ Create LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 6️⃣ Format retrieved docs to show sources
def format_matches(matches: List[Dict]) -> str:
    combined: List[str] = []
    for m in matches:
        md = m.get("metadata", {}) or {}
        text = (md.get("text") or "").strip().replace("\n", " ")
        src = md.get("file_name", md.get("source", "Unknown Source"))
        if not text:
            continue
        combined.append(f"[{src}]\n{text}")
    return "\n\n".join(combined)

# 7️⃣ Build Retrieval-Augmented Generation (RAG) chain (manual retrieval)
def run_rag(query: str) -> str:
    matches = retrieve_context(query, top_k=5)
    context = format_matches(matches)
    prompt_text = prompt.format(context=context, question=query)
    result = llm.invoke(prompt_text)
    return StrOutputParser().invoke(result)

# 8️⃣ Function to get legal answer
def get_legal_answer(query: str):
    try:
        response = run_rag(query)
        return response
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# 9️⃣ Run from terminal
if __name__ == "__main__":
    print("🔎 Ask your legal question (type 'exit' to quit)\n")
    while True:
        query = input("👉 ")
        if query.lower().strip() == "exit":
            print("👋 Exiting LegaBot.")
            break
        print("\n🧾 Answer:\n", get_legal_answer(query))
        print("\n" + "-" * 80 + "\n")
