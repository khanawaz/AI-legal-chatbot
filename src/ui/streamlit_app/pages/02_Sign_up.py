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
from src.ui.streamlit_app.components.auth import set_user, get_user
from src.ui.streamlit_app.components.styling import apply_custom_styling
from src.auth.auth_service import signup_email_password, current_user

st.set_page_config(page_title="Sign up – LegaBot", page_icon="🆕", layout="centered")
apply_custom_styling()

if get_user():
    st.switch_page("main.py")

st.markdown("<div style='max-width:520px;margin:0 auto;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;margin-bottom:1.25rem;'>", unsafe_allow_html=True)
show_logo_or_title()
st.markdown("<h2>🆕 Create Account</h2><p>Join LegaBot and start your legal research</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

with st.form("signup_form", clear_on_submit=False, border=True):
    full_name = st.text_input("Full Name", placeholder="John Doe")
    email = st.text_input("Email", placeholder="you@example.com")
    c1, c2 = st.columns(2)
    with c1:
        pwd = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
    with c2:
        confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
    agree = st.checkbox("I agree to the Terms & Privacy Policy")
    submit = st.form_submit_button("Create account", type="primary", use_container_width=True)

if submit:
    if not agree:
        st.warning("Please agree to the Terms to continue.")
    elif not full_name.strip():
        st.warning("Please enter your full name.")
    elif not email.strip():
        st.warning("Please enter your email.")
    elif len(pwd) < 6:
        st.warning("Password must be at least 6 characters.")
    elif pwd != confirm:
        st.warning("Passwords do not match.")
    else:
        ok, msg = signup_email_password(email.strip(), pwd, full_name.strip())
        if ok:
            u = current_user()
            if u:
                set_user(u)
            st.success("Signup successful. Check email if confirmation is enabled.")
            st.info("We sent you a verification email. Please confirm your email, then return to Login.")
            st.toast("Welcome!", icon="👋")
            time.sleep(0.5)
            st.switch_page("main.py")
        else:
            st.error(msg)

st.markdown("</div>", unsafe_allow_html=True)
