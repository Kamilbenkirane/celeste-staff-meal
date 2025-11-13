"""Image input primitive - reusable file upload and camera input component."""

import streamlit as st
from PIL import Image


def render_image_input(
    key_prefix: str,
    file_label: str = "Télécharger une image",
    camera_label: str = "Prendre une photo",
    file_help: str = "Télécharger une image",
    camera_help: str = "Prendre une photo avec la caméra",
    preview_caption: str | None = None,
    preview_width: int = 300,
    toggle_to_camera_label: str | None = None,
    toggle_to_file_label: str | None = None,
) -> Image.Image | None:
    """Render image input with single mode toggle (file upload OR camera).

    Args:
        key_prefix: Unique prefix for Streamlit keys (e.g., "qr_reader", "validator").
        file_label: Label for file uploader.
        camera_label: Label for camera input.
        file_help: Help text for file uploader.
        camera_help: Help text for camera input.
        preview_caption: Caption for image preview. If None, auto-generates from source.
        preview_width: Width of preview image in pixels.
        toggle_to_camera_label: Custom label for toggle button when switching to camera mode.
        toggle_to_file_label: Custom label for toggle button when switching to file mode.

    Returns:
        PIL Image object if image provided, None otherwise.
    """
    # Initialize input mode in session state (default to "file")
    mode_key = f"{key_prefix}_input_mode"
    if mode_key not in st.session_state:
        st.session_state[mode_key] = "file"

    current_mode = st.session_state[mode_key]

    # Render only the selected input method
    image = None
    source = None

    if current_mode == "file":
        st.markdown("**📁 Depuis un fichier:**")
        uploaded_file = st.file_uploader(
            file_label,
            type=["png", "jpg", "jpeg", "gif", "bmp", "webp"],
            key=f"{key_prefix}_upload",
            help=file_help,
        )
        if uploaded_file:
            image = Image.open(uploaded_file)
            source = "fichier"

        # Toggle button below file uploader
        toggle_label = toggle_to_camera_label or "📷 Passer à la caméra"
        toggle_help = "Basculer vers la caméra pour prendre une photo"
    else:
        st.markdown("**📷 Depuis la caméra:**")
        camera_image = st.camera_input(
            camera_label,
            key=f"{key_prefix}_camera",
            help=camera_help,
        )
        if camera_image:
            image = Image.open(camera_image)
            source = "caméra"

        # Toggle button below camera input
        toggle_label = toggle_to_file_label or "📁 Passer au fichier"
        toggle_help = "Basculer vers le téléchargement de fichier"

    # Toggle button to switch between modes (below the input)
    if st.button(toggle_label, width="stretch", help=toggle_help, key=f"{key_prefix}_toggle"):
        st.session_state[mode_key] = "camera" if current_mode == "file" else "file"
        st.rerun()

    # Display preview if image exists
    if image:
        caption = preview_caption or f"Image ({source})"
        st.image(image, caption=caption, width=preview_width)

    return image


__all__ = ["render_image_input"]
