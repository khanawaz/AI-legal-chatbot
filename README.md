Perfect — since your project now includes **Streamlit UI**, **Chainlit chat**, and **Supabase integration**, here’s your **final deploy-ready setup**:

---

## ✅ `requirements.txt`

```txt
# Core environment
python-dotenv>=1.0.1
pathlib
requests

# Streamlit UI
streamlit>=1.39.0

# Chainlit conversational UI
chainlit>=1.2.0

# Database and Auth
SQLAlchemy>=2.0.23
passlib[bcrypt]>=1.7.4
PyJWT>=2.9.0
supabase>=2.4.0
psycopg2-binary>=2.9.9

# AI + LLM components
sentence-transformers>=2.5.1
torch>=2.3.0
numpy>=1.26.0
scikit-learn>=1.5.2

# Vector DB (if using Pinecone)
pinecone-client>=3.1.0

# Misc tools
tqdm
typing-extensions
```

---

## ✅ `.gitignore`

```gitignore
# --- Python ---
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.db
*.sqlite3

# --- Environments ---
.env
.venv/
venv/
env/
.idea/
.vscode/
.DS_Store

# --- Streamlit & Chainlit ---
.streamlit/secrets.toml
.chainlit/
.chainlit.db

# --- Cache / Logs ---
*.log
*.tmp
*.bak
*.swp
.cache/
__pycache__/
pip-wheel-metadata/

# --- Model weights ---
*.pt
*.bin
*.pkl

# --- Notebooks ---
*.ipynb_checkpoints/

# --- Build / dist ---
dist/
build/
*.egg-info/
*.egg

# --- OS / Editor Junk ---
Thumbs.db
ehthumbs.db
Desktop.ini

# --- Images / uploads ---
assets/
uploads/
*.png
*.jpg
*.jpeg
*.gif
```

---

## ✅ `README.md`

````markdown
# ⚖️ LegaBot – Indian Legal Research Assistant

LegaBot is an **AI-powered legal assistant** that answers questions about the **Indian Penal Code (IPC)**, **Criminal Procedure Code (CrPC)**, and **landmark judgments**.  
Built using **Streamlit** (modern dashboard) and **Chainlit** (chat assistant) with **Supabase Auth** for user login and signup.

---

## 🚀 Features

- 🔐 **Supabase Authentication**
  - Signup, Login, Logout (with email verification)
  - Optional resend confirmation emails
- 💬 **Chat UI via Chainlit**
  - Natural conversation with legal Q&A
  - Smart actions, modals, and context retention
- 🧠 **LLM-based Legal Search**
  - Uses Sentence Transformers for retrieval
  - Torch-based local inference
- 🖥️ **Streamlit UI**
  - Separate login, signup, logout pages
  - Styled dashboard with Q&A area and examples
- ☁️ **Supabase/Postgres backend**
  - User accounts, profile table, session management

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| Frontend | Streamlit + Chainlit |
| Backend | Python (Flask-free, local runtime) |
| Auth | Supabase (email + password) |
| Embeddings | SentenceTransformers `all-MiniLM-L6-v2` |
| Vector DB | Pinecone (optional) |
| Database | PostgreSQL (Supabase-hosted) |

---

## ⚙️ Installation

```bash
git clone https://github.com/<your-username>/AI-legal-chatbot.git
cd AI-legal-chatbot
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
````

---

## 🔑 Environment Setup

Create a `.env` in your project root:

```env
SUPABASE_URL=https://<your-supabase-project>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
DATABASE_URL=postgresql://postgres:<password>@db.<supabase_id>.supabase.co:5432/postgres
AUTH_SECRET_KEY=change-this-very-long-random-string
AUTH_TOKEN_TTL_SECONDS=86400
PINECONE_API_KEY=<optional>
PINECONE_INDEX_NAME=<optional>
```

---

## ▶️ Run Locally

### 🧠 Chainlit (Chat Interface)

```bash
chainlit run src/ui/app.py -w
```

### 🖥️ Streamlit (Web Dashboard)

```bash
streamlit run src/ui/streamlit_app/main.py
```

Visit:

* Chainlit UI → [http://localhost:8000](http://localhost:8000)
* Streamlit UI → [http://localhost:8501](http://localhost:8501)

---

## 🧑‍💻 Development Notes

* Make sure `.env` is **not committed** (already ignored).
* Assets like logos can be placed in `/assets/` if you later add one.
* For email verification issues, disable it in **Supabase Auth → Email Provider Settings** during development.
* To deploy:

  * Streamlit → Streamlit Cloud or Render
  * Chainlit → Docker / Railway / EC2
  * Supabase handles auth + database remotely.

---

## 📂 Project Structure

```
src/
├── auth/
│   ├── auth_service.py
│   ├── supabase_client.py
├── llm/
│   └── rag_pipeline.py
└── ui/
    ├── app.py                # Chainlit main file
    └── streamlit_app/
        ├── main.py
        ├── components/
        │   ├── brand.py
        │   ├── auth.py
        │   └── styling.py
        └── pages/
            ├── 01_🔑_Login.py
            ├── 02_🆕_Sign_up.py
            └── 03_🚪_Logout.py
```

---

## 🛠️ License

MIT License © 2025 [Your Name]

---

```

---

```
