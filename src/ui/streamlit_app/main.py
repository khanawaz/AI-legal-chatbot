# --- path bootstrap (must be first) ---
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # <project>
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import os
import streamlit as st
from src.ui.streamlit_app.components.brand import show_logo_or_title
from src.ui.streamlit_app.components.auth import get_user, guard_auth, logout_with_confirm
from src.ui.streamlit_app.components.styling import apply_custom_styling, answer_card
from src.llm.rag_pipeline import get_legal_answer

st.set_page_config(page_title="LegaBot – Home", page_icon="⚖️", layout="wide")
apply_custom_styling()

# Top bar
c1, c2, c3 = st.columns([0.9, 4, 1.4])
with c1: show_logo_or_title()
with c2:
    st.markdown("### ⚖️ LegaBot – Indian Legal Research Assistant")
    st.caption("Ask about IPC, CrPC, and landmark judgments.")
with c3:
    user = get_user()
    if user:
        st.caption(f"Signed in as **{user.get('email','')}**")
        logout_with_confirm()
    else:
        if st.button("Login / Sign up", type="primary", use_container_width=True):
            st.switch_page("pages/01_Login.py")

st.divider()
guard_auth()  # redirect if not logged in

# Ask UI
st.subheader("Ask a legal question")
query = st.text_area("Your question", placeholder="e.g., What is theft under IPC?", height=140)
cc1, cc2 = st.columns([1.2, 1])
with cc1:
    run = st.button("Ask", type="primary", use_container_width=True)
with cc2:
    clear = st.button("Clear", use_container_width=True)

if clear:
    st.session_state.pop("last_answer", None)
    st.session_state.pop("last_query", None)
    st.rerun()

if run:
    if not query.strip():
        st.warning("Please enter a valid question.")
    else:
        st.session_state["last_query"] = query.strip()
        with st.spinner("Searching legal documents and generating answer..."):
            try:
                st.session_state["last_answer"] = get_legal_answer(query.strip())
                st.toast("Answer ready.", icon="✅")
            except Exception as e:
                st.session_state["last_answer"] = f"⚠️ Error: {e}"
        st.rerun()

if "last_answer" in st.session_state and st.session_state["last_answer"]:
    st.markdown("#### Answer")
    answer_card(st.session_state["last_answer"])

# Sidebar examples
with st.sidebar:
    st.markdown("### 💡 Examples")
    for ex in [
        "What is theft under IPC?",
        "Punishment for murder?",
        "What section deals with bail?",
    ]:
        if st.button(ex, use_container_width=True):
            st.session_state["last_query"] = ex
            with st.spinner("Generating answer..."):
                try:
                    st.session_state["last_answer"] = get_legal_answer(ex)
                except Exception as e:
                    st.session_state["last_answer"] = f"⚠️ Error: {e}"
            st.rerun()

    pinecone_idx = os.getenv("PINECONE_INDEX_NAME", "")
    if pinecone_idx:
        st.markdown(f"**Index:** `{pinecone_idx}`")
