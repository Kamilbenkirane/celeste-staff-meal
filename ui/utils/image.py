"""Image utility functions for UI components."""

import io

from PIL import Image


def pil_image_to_bytes(image: Image.Image, format: str = "PNG") -> io.BytesIO:
    """Convert PIL Image to bytes buffer for Streamlit.

    Args:
        image: PIL Image object to convert.
        format: Image format (default: PNG).

    Returns:
        BytesIO buffer with image data, positioned at start.
    """
    img_bytes = io.BytesIO()
    image.save(img_bytes, format=format)
    img_bytes.seek(0)
    return img_bytes


__all__ = ["pil_image_to_bytes"]
