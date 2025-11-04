import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parents[0] / ".env")

load_dotenv()  # Load your .env file

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY")[:10])
print("PINECONE_API_KEY:", os.getenv("PINECONE_API_KEY")[:10])
