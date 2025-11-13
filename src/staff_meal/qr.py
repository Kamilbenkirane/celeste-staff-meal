"""QR code service for encoding and decoding orders."""

import json
from pathlib import Path

import qrcode  # type: ignore[import-untyped]
import zxingcpp  # type: ignore[import-not-found]
from PIL import Image

from staff_meal.models import Item, Order, OrderItem, OrderSource


def decode_qr(image_path: str | Path) -> Order:
    """Decode QR code from image and return Order object.

    Args:
        image_path: Path to QR code image file.

    Returns:
        Order object parsed from QR code data.

    Raises:
        ValueError: If QR code cannot be decoded or data is invalid.
    """
    image = Image.open(image_path)
    results = zxingcpp.read_barcodes(image)

    if not results:
        msg = f"No QR code found in image: {image_path}"
        raise ValueError(msg)

    # Get first QR code data
    qr_data = results[0].text

    # Parse JSON
    order_dict = json.loads(qr_data)

    # Convert to Order model
    items = [
        OrderItem(
            item=Item(order_item["item"]),
            quantity=order_item["quantity"],
        )
        for order_item in order_dict["items"]
    ]

    return Order(
        order_id=order_dict["order_id"],
        source=OrderSource(order_dict["source"]),
        items=items,
    )


def generate_qr(order: Order, output_path: str | Path | None = None) -> Image.Image:
    """Generate QR code from Order object.

    Args:
        order: Order object to encode.
        output_path: Optional path to save QR code image. If None, returns image object.

    Returns:
        PIL Image object with QR code.
    """
    # Convert Order to JSON
    order_dict = {
        "order_id": order.order_id,
        "source": order.source.value,
        "items": [
            {"item": item.item.value, "quantity": item.quantity} for item in order.items
        ],
    }

    json_data = json.dumps(order_dict, ensure_ascii=False)

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if output_path:
        img.save(output_path)

    return img  # type: ignore[no-any-return]
