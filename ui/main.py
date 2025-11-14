"""Main orchestration for Celeste Staff Meal Streamlit UI."""

import streamlit as st

from ui.components.ai_config import render_ai_config_sidebar
from ui.components.dashboard import render_dashboard
from ui.components.order_list import render_order_list
from ui.components.order_validator import render_order_validator
from ui.components.qr_generator import render_qr_generator


def render() -> None:
    """Main render function - orchestrates the entire UI."""
    # Page config
    st.set_page_config(
        page_title="Celeste Staff Meal",
        layout="wide",
        page_icon="🍽️",
    )

    # Initialize navigation state
    if "page" not in st.session_state:
        st.session_state.page = "validation"

    # Sidebar - Navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        if st.button("✅ Validation", width="stretch", type="primary" if st.session_state.page == "validation" else "secondary"):
            st.session_state.page = "validation"
            st.rerun()
        if st.button("📊 Tableau de bord", width="stretch", type="primary" if st.session_state.page == "dashboard" else "secondary"):
            st.session_state.page = "dashboard"
            st.rerun()
        if st.button("📝 Mode démo", width="stretch", type="primary" if st.session_state.page == "demo" else "secondary"):
            st.session_state.page = "demo"
            st.rerun()
        if st.button("📋 Commandes sauvegardées", width="stretch", type="primary" if st.session_state.page == "orders" else "secondary"):
            st.session_state.page = "orders"
            st.rerun()

        st.divider()

        # AI Configuration
        render_ai_config_sidebar()

    # Title - large and clear for kitchen use
    st.markdown(
        '<div style="text-align: center; font-size: 48px; font-weight: bold; margin: 20px 0;">🍽️ Celeste Staff Meal</div>',
        unsafe_allow_html=True,
    )

    # Main content routing
    if st.session_state.page == "dashboard":
        render_dashboard()
    elif st.session_state.page == "demo":
        render_qr_generator()
    elif st.session_state.page == "orders":
        render_order_list()
    else:  # validation (default)
        st.markdown(
            '<div style="text-align: center; font-size: 20px; margin-bottom: 20px;">Valider la commande</div>',
            unsafe_allow_html=True,
        )
        st.divider()
        render_order_validator()


__all__ = ["render"]
