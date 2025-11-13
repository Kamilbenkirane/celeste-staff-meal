"""Service layer for Celeste Staff Meal UI - QR code operations."""

import io
import tempfile
from pathlib import Path

from PIL import Image

from staff_meal.models import Order
from staff_meal.qr import decode_qr
from ui.services.prediction import predict_order
from ui.services.validation import compare_orders


def read_qr_order(qr_image: Image.Image | bytes | None) -> Order:
    """Read order from QR code image.

    Args:
        qr_image: QR code image (PIL Image, bytes, or None).

    Returns:
        Order object parsed from QR code.

    Raises:
        ValueError: If QR code cannot be decoded or is not recognized.
    """
    if qr_image is None:
        msg = "QR code non reconnu"
        raise ValueError(msg)

    # Save QR image to temp file for decoding
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        qr_path = tmp.name
        if isinstance(qr_image, Image.Image):
            qr_image.save(qr_path)
        elif isinstance(qr_image, bytes):
            img = Image.open(io.BytesIO(qr_image))
            img.save(qr_path)
        else:
            msg = f"QR code non reconnu: type {type(qr_image)} non supporté"
            raise ValueError(msg)

    try:
        # Decode QR code to get order
        order = decode_qr(qr_path)
        return order
    except (ValueError, KeyError, TypeError) as e:
        msg = "QR code non reconnu"
        raise ValueError(msg) from e
    finally:
        # Clean up temp file
        Path(qr_path).unlink(missing_ok=True)


__all__ = ["read_qr_order", "predict_order", "compare_orders"]
