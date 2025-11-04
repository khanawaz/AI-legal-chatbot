import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
# Optional lottie support: prefer streamlit_lottie if installed, otherwise provide a minimal fallback.
try:
    from streamlit_lottie import st_lottie
except Exception:
    import json as _json
    import base64 as _base64
    import streamlit.components.v1 as _components

    def st_lottie(lottie_data, height=240, key=None, loop=True):
        """Fallback renderer for Lottie animations using the lottie-player web component."""
        if not lottie_data:
            return None
        try:
            if isinstance(lottie_data, dict):
                b64 = _base64.b64encode(_json.dumps(lottie_data).encode()).decode()
                src = f"data:application/json;base64,{b64}"
            elif isinstance(lottie_data, str) and (lottie_data.strip().startswith("{") or lottie_data.strip().startswith("[")):
                b64 = _base64.b64encode(lottie_data.encode()).decode()
                src = f"data:application/json;base64,{b64}"
            else:
                # assume it's a URL
                src = lottie_data
            html = f'''
            <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
            <lottie-player src="{src}" background="transparent" speed="1" {"loop" if loop else ""} autoplay style="width:100%;height:{height}px;"></lottie-player>
            '''
            return _components.html(html, height=height, key=key)
        except Exception:
            return None

import json
import requests

# Ensure project root is on sys.path and env loaded
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from src.llm.rag_pipeline import get_legal_answer  # noqa: E402


def load_lottie(url: str):
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None


def main() -> None:
    st.set_page_config(page_title="LegaBot - Indian Legal Assistant", page_icon="⚖️", layout="wide")

    # Theme auto-follow via CSS respects user system preference
    st.markdown(
        """
        <style>
          @media (prefers-color-scheme: dark) {
            :root { color-scheme: dark; }
          }
          .stButton>button[kind="primary"] { transition: transform .08s ease; }
          .stButton>button[kind="primary"]:active { transform: scale(0.98); }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("⚖️ LegaBot – Indian Legal Research Assistant")
    st.markdown(
        """
        Ask questions about IPC/CrPC and landmark judgments. Answers are generated via RAG over your indexed documents.
        """
    )

    with st.sidebar:
        st.header("Configuration")
        pinecone_idx = os.getenv("PINECONE_INDEX_NAME", "")
        st.markdown(f"**Pinecone Index:** `{pinecone_idx or 'not set'}`")
        st.markdown("---")
        st.subheader("Examples")
        examples = [
            "What is theft under IPC?",
            "Punishment for murder?",
            "What section deals with bail?",
        ]
        for ex in examples:
            if st.button(ex, use_container_width=True):
                st.session_state["query"] = ex

    lottie = load_lottie("https://assets4.lottiefiles.com/packages/lf20_qp1q7mct.json")

    left, right = st.columns([6, 5])
    with left:
        query = st.text_area("Enter your question", value=st.session_state.get("query", ""), height=100)
        col1, col2, col3 = st.columns([1.2, 1, 6])
        with col1:
            run = st.button("Ask", type="primary", use_container_width=True)
        with col2:
            clear = st.button("Clear", use_container_width=True)
        with col3:
            system_theme = st.toggle("Follow system theme", value=True)
    with right:
        if lottie:
            st_lottie(lottie, height=240, key="header_anim", loop=True)
        else:
            st.empty()

    if clear:
        st.session_state.pop("query", None)
        st.rerun()

    if run:
        if not query.strip():
            st.warning("Please enter a valid question.")
            return
        with st.spinner("Searching legal documents and generating answer..."):
            answer = get_legal_answer(query.strip())

        # Answer card
        st.subheader("Answer")
        st.markdown(
            f"""
            <div style="padding:16px;border-radius:12px;background:var(--secondary-background-color,#f6f7fb);">
                {answer}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Copy to clipboard (simple approach)
        st.code(answer if isinstance(answer, str) else str(answer))


if __name__ == "__main__":
    main()


