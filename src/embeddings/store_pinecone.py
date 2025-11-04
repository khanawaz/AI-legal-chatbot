# 📁 File: src/embeddings/store_pinecone.py
# Purpose: Upload embeddings + small metadata to Pinecone safely

import os
import numpy as np
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ✅ 1. Load environment variables from .env in project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

API_KEY = os.getenv("PINECONE_API_KEY")
ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

print(f"🔑 API Key loaded: {API_KEY[:15]}")  # partially hidden for safety

# ✅ 2. Connect to Pinecone
pc = Pinecone(api_key=API_KEY)

# ✅ 3. Create the index if it doesn’t exist
if INDEX_NAME not in [index.name for index in pc.list_indexes()]:
    print(f"📦 Creating a new Pinecone index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # matches all-MiniLM-L6-v2 model
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# ✅ 4. Connect to index
index = pc.Index(INDEX_NAME)

# ✅ 5. Load your legal data and embeddings
DATA_FILE = PROJECT_ROOT / "Data" / "legal_text.csv"
EMBED_FILE = PROJECT_ROOT / "Data" / "legal_embeddings.npy"

df = pd.read_csv(DATA_FILE)
embeddings = np.load(EMBED_FILE)

print(f"📚 Loaded {len(df)} text entries and {len(embeddings)} embeddings")

# ✅ 6. Double-check model dimension
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f"🧠 Embedding dimension from model: {model.get_sentence_embedding_dimension()}")

# ✅ 7. Upload to Pinecone (safe metadata size + batching)
print("🚀 Uploading embeddings to Pinecone...")

vectors = []
for i, emb in enumerate(embeddings):
    # Keep metadata small (max 40 KB)
    snippet = df.iloc[i]["text"][:800]  # first 800 characters
    vectors.append((
        str(i),
        emb.tolist(),
        {
            "text": snippet,
            "file_name": str(df.iloc[i].get("file_name", "unknown"))
        }
    ))

# Upload in batches of 100 vectors
for i in tqdm(range(0, len(vectors), 100)):
    batch = vectors[i:i+100]
    index.upsert(vectors=batch)
    print(f"✅ Uploaded {i + len(batch)} / {len(vectors)} vectors")

print("🎉 All embeddings uploaded successfully to Pinecone!")