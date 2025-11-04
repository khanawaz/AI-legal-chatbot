# --- path bootstrap ---
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import time
import streamlit as st
from src.ui.streamlit_app.components.brand import show_logo_or_title
from src.ui.streamlit_app.components.auth import get_user, set_user
from src.ui.streamlit_app.components.styling import apply_custom_styling
from src.auth.auth_service import logout

st.set_page_config(page_title="Logout – LegaBot", page_icon="🚪", layout="centered")
apply_custom_styling()

st.markdown("<div style='max-width:520px;margin:0 auto;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;margin-bottom:1.25rem;'>", unsafe_allow_html=True)
show_logo_or_title()
st.markdown("<h2>🚪 Logout</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

user = get_user()
if not user:
    st.info("You are not logged in.")
    if st.button("Go to Login", type="primary", use_container_width=True):
        st.switch_page("pages/01_Login.py")
else:
    st.markdown(f"<div class='card'><strong>Signed in as:</strong> {user.get('email','')}</div>", unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", use_container_width=True):
            st.switch_page("main.py")
    with c2:
        if st.button("Yes, logout", type="primary", use_container_width=True):
            try:
                logout()
            finally:
                set_user(None)
                st.success("Logged out successfully.")
                st.toast("See you soon!", icon="👋")
                time.sleep(0.5)
                st.switch_page("pages/01_Login.py")

st.markdown("</div>", unsafe_allow_html=True)
