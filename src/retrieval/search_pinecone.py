# 📁 File: src/retrieval/search_pinecone.py
# ✅ Clean version — hides similarity numbers

import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
if not PINECONE_API_KEY or not INDEX_NAME:
    raise RuntimeError("Missing PINECONE_API_KEY or PINECONE_INDEX_NAME in .env")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def search_legal_docs(query):
    """Search Pinecone for relevant legal text (no similarity numbers)."""
    query_embedding = model.encode([query]).tolist()[0]
    results = index.query(vector=query_embedding, top_k=5, include_metadata=True)

    print("\n📜 Relevant Legal Sections:\n")

    found = False
    for match in results["matches"]:
        text = match["metadata"]["text"].strip()
        score = match["score"]

        if score > 0.6 and len(text) > 50:
            found = True
            print(f"🔹 {text[:500]}...\n")  # ✅ No numbers shown

    if not found:
        print("⚠️ No relevant matches found.")

if __name__ == "__main__":
    print("🔎 Ask your legal question (or type 'exit'):")
    while True:
        query = input("👉 ").strip()
        if query.lower() == "exit":
            print("👋 Goodbye!")
            break
        elif query == "":
            print("Please enter a valid question.")
        else:
            search_legal_docs(query)
