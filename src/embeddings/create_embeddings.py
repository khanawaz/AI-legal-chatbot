# 📁 File: src/embeddings/create_embeddings.py

from sentence_transformers import SentenceTransformer
import pandas as pd
from tqdm import tqdm
import numpy as np
from pathlib import Path

# Step 1 — Load the extracted text
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "Data" / "legal_text.csv"
df = pd.read_csv(DATA_FILE)

# Step 2 — Load the model (it converts text → embeddings)
print("🧠 Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Step 3 — Create embeddings
texts = df['text'].tolist()
embeddings = []

print("🔢 Creating embeddings...")
for text in tqdm(texts):
    emb = model.encode(text)
    embeddings.append(emb)

# Step 4 — Save embeddings
embeddings = np.array(embeddings)
OUTPUT = PROJECT_ROOT / "Data" / "legal_embeddings.npy"
np.save(OUTPUT, embeddings)
print(f"💾 Saved embeddings to {OUTPUT}")
