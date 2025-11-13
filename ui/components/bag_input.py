"""Bag image input component - composed component for bag photo input."""

import streamlit as st
from PIL import Image

from ui.components.input import render_image_input


def render_bag_image_input(
    key_prefix: str,
    title: str = "📸 Image de la commande",
) -> Image.Image | None:
    """Render bag image input section.

    Args:
        key_prefix: Unique prefix for Streamlit keys (e.g., "validator").
        title: Section title.

    Returns:
        PIL Image object if image provided, None otherwise.
    """
    if title:
        st.markdown(f"##### {title}")

    # Render image input with bag-specific labels
    bag_image = render_image_input(
        key_prefix=f"{key_prefix}_bag",
        file_label="Télécharger une image",
        camera_label="Prendre une photo",
        file_help="Télécharger l'image de la commande",
        camera_help="Prendre une photo de la commande avec la caméra",
        preview_caption="Image de la commande",
        toggle_to_camera_label="📷 Prendre en photo la commande",
        toggle_to_file_label="📁 Importer une image de la commande",
    )

    return bag_image


__all__ = ["render_bag_image_input"]
