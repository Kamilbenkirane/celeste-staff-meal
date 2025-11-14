"""Service layer for order prediction using Celeste image intelligence."""

import io

from PIL import Image

from celeste import create_client
from celeste.artifacts import ImageArtifact
from celeste.core import Capability
from staff_meal.models import Item, Order
from ui.services.client_config import get_client_config


async def predict_order_async(bag_image: Image.Image, expected_order: Order | None = None) -> Order:
    """Detect order from bag image using Celeste image intelligence.

    Args:
        bag_image: PIL Image of bag contents.
        expected_order: Optional expected order to extract order_id and source from.

    Returns:
        Detected Order object.

    Raises:
        ValueError: If image is None or invalid, or if no valid items detected.
    """
    if bag_image is None:
        msg = "Bag image cannot be None"
        raise ValueError(msg)

    # Convert PIL Image to ImageArtifact
    img_bytes = io.BytesIO()
    bag_image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    image_artifact = ImageArtifact(data=img_bytes.read())

    # Get client configuration from session state
    provider, model, api_key = get_client_config(
        Capability.IMAGE_INTELLIGENCE,
        default_provider="google",
        default_model="gemini-2.5-flash-lite",
    )

    # Create Celeste image intelligence client
    client = create_client(
        capability=Capability.IMAGE_INTELLIGENCE,
        provider=provider,
        model=model.id,
        api_key=api_key,
    )

    # Build comprehensive prompt with context
    prompt_parts = [
        "You are analyzing a restaurant order bag image to verify that all items are present.",
        "Detect all order items visible in the image and identify each item with its exact quantity.",
        "",
        "Available menu items:",
        *[f"- {item.value}" for item in Item],
        "",
        "CRITICAL COUNTING INSTRUCTIONS:",
        "- Count BOXES, CONTAINERS, or PACKAGES, NOT individual pieces inside containers",
        "- If you see a box containing multiple items, count it as 1 box, not multiple individual items",
        "- For example: If you see 'Boite de 6 California Saumons', count it as 1 box, not 6 individual pieces",
        "- The item names already indicate the packaging format (e.g., 'Boite de 6 California Saumons' means boxes of 6)",
        "",
        "Important instructions:",
        "- Use only the exact item names from the list above",
        "- Count precisely the quantities of boxes/containers visible in the image",
        "- Ignore items that are not in the available items list",
        "- Match the packaging format exactly as specified in the item names",
    ]

    if expected_order:
        prompt_parts.extend([
            "",
            f"Expected order (ID: {expected_order.order_id}, Source: {expected_order.source.value}):",
            *[f"- {item.quantity}x {item.item.value}" for item in expected_order.items],
            "",
            "Verify that the detected items match this order.",
        ])

    prompt = "\n".join(prompt_parts)

    # Call generate with structured output schema
    output = await client.generate(
        image=image_artifact,
        prompt=prompt,
        thinking_budget=0,
        output_schema=Order,
    )

    # Extract detected order from output
    detected_order: Order = output.content

    # Use expected order's ID and source if provided, otherwise use detected values
    if expected_order:
        detected_order.order_id = expected_order.order_id
        detected_order.source = expected_order.source

    # Filter out invalid quantities (<= 0) if any
    valid_items = [item for item in detected_order.items if item.quantity > 0]
    if not valid_items:
        msg = "No valid items detected"
        raise ValueError(msg)

    # Return order with valid items only
    return Order(
        order_id=detected_order.order_id,
        source=detected_order.source,
        items=valid_items,
    )


def predict_order(bag_image: Image.Image, expected_order: Order | None = None) -> Order:
    """Synchronous wrapper for predict_order_async.

    Args:
        bag_image: PIL Image of bag contents.
        expected_order: Optional expected order to extract order_id and source from.

    Returns:
        Detected Order object.

    Raises:
        ValueError: If image is None or invalid, or if no valid items detected.
    """
    from ui.utils import runner

    return runner.run(predict_order_async(bag_image, expected_order))  # type: ignore[no-any-return]


__all__ = ["predict_order", "predict_order_async"]
