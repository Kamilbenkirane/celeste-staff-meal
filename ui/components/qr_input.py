"""QR code input component - composed component for QR code reading."""

import streamlit as st
from PIL import Image

from staff_meal.models import Order
from ui.components.input import render_image_input
from ui.services import read_qr_order


def render_qr_input_section(
    key_prefix: str,
    title: str = "📤 Télécharger un QR Code",
) -> tuple[Image.Image | None, Order | None, str | None]:
    """Render QR input section and handle reading.

    Args:
        key_prefix: Unique prefix for Streamlit keys (e.g., "qr_reader", "validator").
        title: Section title.

    Returns:
        Tuple of (qr_image, order, error_message).
        - qr_image: PIL Image if provided, None otherwise.
        - order: Order object if read successfully, None otherwise.
        - error_message: Error message if reading failed, None otherwise.
    """
    if title:
        st.markdown(f"#### {title}")

    # Render image input
    qr_image = render_image_input(
        key_prefix=key_prefix,
        file_label="Télécharger une image",
        camera_label="Prendre une photo",
        file_help="Télécharger la photo du QR code",
        camera_help="Prendre une photo du QR code avec la caméra",
        preview_caption="QR Code",
        toggle_to_camera_label="📷 Scanner un QR code",
        toggle_to_file_label="📁 Importer un QR code",
    )

    # Read QR button
    st.divider()
    read_clicked = st.button(
        "🔍 LIRE QR CODE",
        type="primary",
        width="stretch",
        help="Lire les informations du QR code",
        disabled=qr_image is None,
        key=f"{key_prefix}_read_qr",
    )

    # Handle QR reading
    order: Order | None = None
    error_message: str | None = None

    if read_clicked:
        if qr_image is None:
            error_message = "⚠️ Veuillez télécharger une image de QR code"
        else:
            with st.spinner("🔍 Lecture du QR code..."):
                try:
                    order = read_qr_order(qr_image)
                except ValueError as e:
                    error_message = str(e)

    return (qr_image, order, error_message)


__all__ = ["render_qr_input_section"]
