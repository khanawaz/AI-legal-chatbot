# src/ui/streamlit_app.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Optional lottie (with graceful fallback)
try:
    from streamlit_lottie import st_lottie
except Exception:
    import json as _json
    import base64 as _base64
    import streamlit.components.v1 as _components
    def st_lottie(lottie_data, height=240, key=None, loop=True):
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

# ----- Project setup & env -----
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from src.llm.rag_pipeline import get_legal_answer  # noqa: E402
from src.auth.auth_service import (
    signup_email_password,
    login_email_password,
    current_user,
    logout,
)
def st_current_user():
    user = current_user()
    if user:
        st.session_state["user"] = user
        return user
    return st.session_state.get("user")

def st_login(email: str, password: str):
    try:
        resp = login_email_password(email, password)
        user = current_user()
        if user:
            st.session_state["user"] = user
            return True, "Login successfull"
        return False, "Login succeeded but no session found"
    except Exception as e:
        return False, f"Login failed: {e}"

def st_logout():
    try:
        logout()
    except Exception:
        pass
    st.session_state.pop("user", None)


def load_lottie(url: str):
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None

def auth_sidebar():
    user = st_current_user()
    if user:
        st.success(f"Signed in as **{user.get('email','')}**")
        if st.button("Logout", use_container_width=True):
            st_logout()
            st.rerun()
        st.markdown("---")
        return True

    tabs = st.tabs(["Login", "Sign up"])
    with tabs[0]:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Password", type="password", key="login_pwd")
            submitted = st.form_submit_button("Login")
        if submitted:
            ok, msg = st_login(email, pwd)
            if ok:
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(msg)

    with tabs[1]:
        with st.form("signup_form", clear_on_submit=False):
            name = st.text_input("Full name", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            pwd = st.text_input("Password (min 6 chars)", type="password", key="signup_pwd")
            submitted = st.form_submit_button("Create account")
        if submitted:
            ok, msg = signup_email_password(email, pwd, name)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    return False

def main() -> None:
    """Main entry point for the Streamlit app (legacy - use streamlit_app/main.py instead)"""
    # Redirect to the new main.py structure
    st.set_page_config(page_title="LegaBot - Indian Legal Assistant", page_icon="⚖️", layout="wide")
    st.info("ℹ️ This is the legacy entry point. Please use `streamlit run src/ui/streamlit_app/main.py` instead.")
    st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>Redirecting to new interface...</h2>
            <p>Please run: <code>streamlit run src/ui/streamlit_app/main.py</code></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Try to redirect if possible
    try:
        st.switch_page("streamlit_app/main.py")
    except:
        pass

if __name__ == "__main__":
    main()
