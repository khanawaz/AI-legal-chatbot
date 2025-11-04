# --- path bootstrap ---
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import streamlit as st
from src.ui.streamlit_app.components.brand import show_logo_or_title
from src.ui.streamlit_app.components.auth import set_user, get_user
from src.ui.streamlit_app.components.styling import apply_custom_styling
from src.auth.auth_service import login_email_password, current_user

st.set_page_config(page_title="Login – LegaBot", page_icon="🔑", layout="centered")
apply_custom_styling()

# Already logged in? go home
if get_user():
    st.switch_page("main.py")

st.markdown("<div style='max-width:520px;margin:0 auto;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;margin-bottom:1.25rem;'>", unsafe_allow_html=True)
show_logo_or_title()
st.markdown("<h2>🔑 Welcome Back</h2><p>Sign in to your LegaBot account</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

with st.form("login_form", clear_on_submit=False, border=True):
    email = st.text_input("Email", placeholder="you@example.com")
    pwd = st.text_input("Password", type="password", placeholder="••••••••")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        submit = st.form_submit_button("Login", type="primary", use_container_width=True)
    with c2:
        st.page_link("pages/02_Sign_up.py", label="Create account →", icon="🆕", use_container_width=True)

if submit:
    if not email.strip() or not pwd.strip():
        st.error("Please fill both email and password.")
    else:
        try:
            login_email_password(email.strip(), pwd)
            u = current_user()
            if u:
                set_user(u)
                st.toast("Logged in.", icon="✅")
                st.switch_page("main.py")
            else:
                st.error("Login succeeded but no active session found.")
        except Exception as e:
            msg = str(e)
            if "invalid" in msg.lower():
                st.error("Invalid email or password.")
            else:
                st.error(f"Login failed: {msg}")

st.markdown("</div>", unsafe_allow_html=True)
