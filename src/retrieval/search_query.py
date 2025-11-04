# 📁 File: src/retrieval/search_query.py

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Load data and embeddings
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEXT_FILE = PROJECT_ROOT / "Data" / "legal_text.csv"
EMBED_FILE = PROJECT_ROOT / "Data" / "legal_embeddings.npy"

print("📚 Loading data...")
df = pd.read_csv(TEXT_FILE)
embeddings = np.load(EMBED_FILE).astype(np.float32)

# Create FAISS index (for fast searching)
dimension = embeddings.shape[1]  # 384 for all-MiniLM-L6-v2
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
print("✅ Index created and embeddings added!")

# Load same model for encoding user queries
model = SentenceTransformer('all-MiniLM-L6-v2')

def search_law(query, top_k=3):
    """Find top_k most similar laws for the query."""
    q_emb = model.encode([query]).astype(np.float32)
    distances, indices = index.search(q_emb, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        law_text = df.iloc[idx]['text']
        score = distances[0][i]
        results.append((law_text, score))
    return results

if __name__ == "__main__":
    while True:
        query = input("\n🔎 Ask your legal question (or type 'exit'): ")
        if query.lower() == "exit":
            break
        
        results = search_law(query)
        print("\n📜 Top Results:\n")
        for i, (law, score) in enumerate(results, 1):
            print(f"{i}. {law[:300]}...")  # Show first 300 characters
