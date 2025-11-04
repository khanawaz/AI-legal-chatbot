# 📁 File: src/ingestion/load_pdfs.py
# ✅ Final Clean + Chunked version

import fitz  # PyMuPDF
import os
import pandas as pd
import re
from pathlib import Path
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:  # fallback for older langchain
    from langchain.text_splitter import RecursiveCharacterTextSplitter

# Folder containing your PDFs
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = PROJECT_ROOT / "Data"
# Output CSV file to store cleaned chunks
OUTPUT_FILE = PROJECT_ROOT / "Data" / "legal_text.csv"

def clean_text(text: str) -> str:
    """
    Remove extra whitespace, page numbers, and other junk text.
    """
    # Replace multiple spaces/newlines with one space
    text = re.sub(r'\s+', ' ', text)

    # Remove patterns like 'Page 1 of 50', 'Page 10', etc.
    text = re.sub(r'Page\s*\d+(\s*of\s*\d+)?', '', text, flags=re.IGNORECASE)

    # Remove weird symbols or formatting
    text = re.sub(r'[•◦▪●]', '', text)

    # Trim leading/trailing spaces
    text = text.strip()
    return text

def extract_text_from_pdfs(pdf_dir: str):
    """
    Extract and clean text from all PDFs, split into chunks.
    """
    data = []

    # Splitter breaks text into small pieces
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,   # each chunk has around 1000 characters
        chunk_overlap=100, # small overlap for context continuity
        separators=["\n\n", "\n", ".", " "]
    )

    for file_name in os.listdir(pdf_dir):
        if not file_name.endswith(".pdf"):
            continue

        pdf_path = os.path.join(pdf_dir, file_name)
        print(f"📖 Reading: {file_name}")

        try:
            with fitz.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf:
                    page_text = page.get_text("text")
                    full_text += clean_text(page_text) + " "
        except Exception as e:
            print(f"⚠️ Error reading {file_name}: {e}")
            continue

        # Skip if text is too short (empty or junk)
        if len(full_text.strip()) < 200:
            print(f"⚠️ Skipping {file_name}: Not enough text")
            continue

        # Split into small, meaningful chunks
        chunks = splitter.split_text(full_text)

        for i, chunk in enumerate(chunks):
            # Skip blank or small meaningless chunks
            if len(chunk.strip()) > 100 and not chunk.isspace():
                data.append({
                    "file_name": file_name,
                    "chunk_id": i,
                    "text": chunk.strip()
                })

    return pd.DataFrame(data)

if __name__ == "__main__":
    print("🚀 Starting PDF extraction and cleaning...")
    df = extract_text_from_pdfs(PDF_DIR)
    print(f"✅ Extracted {len(df)} cleaned text chunks")

    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"💾 Saved cleaned text to {OUTPUT_FILE}")
