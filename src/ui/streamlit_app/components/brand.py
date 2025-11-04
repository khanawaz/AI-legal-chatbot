import streamlit as st
from pathlib import Path
import os

def show_logo_or_title():
    """
    If LEGABOT_LOGO env path exists, show it. Otherwise show a clean text title.
    (No external assets required.)
    """
    p = os.getenv("LEGABOT_LOGO")
    if p and Path(p).exists():
        st.image(p, use_container_width=True)
    else:
        st.markdown("## ⚖️ LegaBot")
