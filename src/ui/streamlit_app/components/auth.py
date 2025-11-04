from typing import Optional
import streamlit as st
from src.auth.auth_service import current_user, logout

SESSION_KEY = "legabot_user"

def get_user() -> Optional[dict]:
    u = current_user()
    if u:
        st.session_state[SESSION_KEY] = u
        return u
    return st.session_state.get(SESSION_KEY)

def set_user(user: Optional[dict]):
    if user:
        st.session_state[SESSION_KEY] = user
    else:
        st.session_state.pop(SESSION_KEY, None)

def guard_auth():
    if not get_user():
        st.switch_page("pages/01_Login.py")

def logout_with_confirm():
    with st.popover("Logout", use_container_width=True):
        st.write("Are you sure you want to logout?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Cancel", use_container_width=True):
                st.rerun()
        with c2:
            if st.button("Yes, logout", type="primary", use_container_width=True):
                try:
                    logout()
                finally:
                    set_user(None)
                    st.toast("Logged out", icon="👋")
                    st.switch_page("pages/01_Login.py")
