"""Order list component - display and select saved orders."""

import streamlit as st

from staff_meal.models import Order
from staff_meal.order_storage import get_all_orders
from staff_meal.qr import generate_qr
from ui.components.output import render_order_details
from ui.utils import runner
from ui.utils.image import pil_image_to_bytes


def render_order_list() -> None:
    """Render list of saved orders with ability to regenerate QR codes."""
    st.markdown(
        '<div style="text-align: center; font-size: 48px; font-weight: bold; margin: 20px 0;">📋 Commandes sauvegardées</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    # Load saved orders
    with st.spinner("Chargement des commandes..."):
        orders = runner.run(get_all_orders(limit=100))

    if not orders:
        st.info("Aucune commande sauvegardée. Créez une commande dans le mode démo pour commencer.")
        return

    st.markdown(f"#### {len(orders)} commande(s) trouvée(s)")
    st.divider()

    # Display each order
    for idx, order in enumerate(orders):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Commande:** {order.order_id}")
                st.markdown(f"**Plateforme:** {order.source.value}")
                st.markdown(f"**Articles:** {len(order.items)} article(s)")

                # Show items summary
                items_summary = ", ".join([f"{item.quantity}x {item.item.value}" for item in order.items[:3]])
                if len(order.items) > 3:
                    items_summary += f" ... (+{len(order.items) - 3} autres)"
                st.markdown(f"*{items_summary}*")

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📱 Régénérer QR", key=f"regenerate_{idx}", width="stretch"):
                    # Generate QR code
                    qr_image = generate_qr(order)

                    # Store in session state for display
                    st.session_state.selected_order = order
                    st.session_state.selected_qr = qr_image
                    st.session_state.show_qr = True

            # Show order details if expanded
            with st.expander(f"Détails de la commande {order.order_id}"):
                render_order_details(order)

            st.divider()

    # Display QR code if one was selected
    if st.session_state.get("show_qr") and "selected_qr" in st.session_state:
        st.markdown("#### 📱 QR Code régénéré")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            img_bytes = pil_image_to_bytes(st.session_state.selected_qr)
            st.image(img_bytes, width=300)

        if "selected_order" in st.session_state:
            render_order_details(st.session_state.selected_order)

        # Download button
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="💾 Télécharger QR Code",
                data=img_bytes,
                file_name=f"qr_{st.session_state.selected_order.order_id}.png",
                mime="image/png",
                width="stretch",
            )
        with col2:
            if st.button("🔄 Fermer", width="stretch"):
                st.session_state.show_qr = False
                if "selected_qr" in st.session_state:
                    del st.session_state.selected_qr
                if "selected_order" in st.session_state:
                    del st.session_state.selected_order


__all__ = ["render_order_list"]
