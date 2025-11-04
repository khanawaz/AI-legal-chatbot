import streamlit as st

def apply_custom_styling():
    st.markdown(
        """
        <style>
        :root{
            --primary-color:#2563eb;--primary-dark:#1e40af;--secondary:#64748b;
            --success:#10b981;--warn:#f59e0b;--error:#ef4444;
            --bg:#ffffff;--bg2:#f8fafc;--bg3:#f1f5f9;--text:#0f172a;--text2:#475569;
            --border:#e2e8f0;--r-sm:.375rem;--r-md:.5rem;--r-lg:.75rem;--r-xl:1rem;
            --shadow-sm:0 1px 2px rgb(0 0 0 / .05);--shadow-md:0 4px 6px -1px rgb(0 0 0 / .1);
        }
        @media (prefers-color-scheme: dark){
            :root{--bg:#0f172a;--bg2:#1e293b;--bg3:#334155;--text:#f1f5f9;--text2:#cbd5e1;--border:#334155;}
        }
        .main .block-container{max-width:1200px;padding-top:1.5rem;padding-bottom:2rem}
        h1,h2,h3{color:var(--text);font-weight:700}
        .stButton>button{border-radius:var(--r-md);padding:.55rem 1.2rem;border:none;box-shadow:var(--shadow-sm);font-weight:600}
        .stButton>button[kind="primary"]{background:linear-gradient(135deg,var(--primary-color),var(--primary-dark));color:#fff}
        .stButton>button[kind="primary"]:hover{transform:translateY(-1px)}
        .stTextInput input,.stTextArea textarea{
            border-radius:var(--r-md);border:1px solid var(--border);padding:.7rem;background:var(--bg);color:var(--text)
        }
        .answer{padding:1.25rem;border-radius:var(--r-xl);background:linear-gradient(135deg,var(--bg2),var(--bg));border:1px solid var(--border)}
        .card{padding:1rem;border:1px solid var(--border);border-radius:var(--r-lg);background:var(--bg2)}
        </style>
        """,
        unsafe_allow_html=True,
    )

def answer_card(html: str):
    st.markdown(f'<div class="answer">{html}</div>', unsafe_allow_html=True)
