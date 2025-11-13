"""Order validation service - compare expected and detected orders."""

from staff_meal.models import ComparisonResult, ItemMatch, ItemMismatch, Order, OrderItem


def compare_orders(expected: Order, detected: Order) -> ComparisonResult:
    """Compare expected and detected orders.

    Args:
        expected: Expected order from QR code.
        detected: Detected order from bag image.

    Returns:
        ComparisonResult with comparison details.
    """
    # Build detected items dict for quick lookup
    detected_items: dict[str, int] = {}
    for item in detected.items:
        detected_items[item.item.value] = item.quantity

    # Compare each expected item
    missing_items: list[ItemMismatch] = []
    too_few_items: list[ItemMismatch] = []
    too_many_items: list[ItemMismatch] = []
    matched_items: list[ItemMatch] = []

    for expected_item in expected.items:
        item_name = expected_item.item.value
        expected_qty = expected_item.quantity
        detected_qty = detected_items.get(item_name, 0)

        is_match = expected_qty == detected_qty

        matched_items.append(
            ItemMatch(
                item=expected_item.item,
                expected_quantity=expected_qty,
                detected_quantity=detected_qty,
                is_match=is_match,
            )
        )

        if not is_match:
            if detected_qty == 0:
                # Item is missing (not detected at all)
                missing_items.append(
                    ItemMismatch(
                        item=expected_item.item,
                        expected_quantity=expected_qty,
                        detected_quantity=0,
                    )
                )
            elif detected_qty < expected_qty:
                # Too few detected
                too_few_items.append(
                    ItemMismatch(
                        item=expected_item.item,
                        expected_quantity=expected_qty,
                        detected_quantity=detected_qty,
                    )
                )
            else:  # detected_qty > expected_qty
                # Too many detected
                too_many_items.append(
                    ItemMismatch(
                        item=expected_item.item,
                        expected_quantity=expected_qty,
                        detected_quantity=detected_qty,
                    )
                )

    # Check for extra items (detected but not expected)
    expected_item_names = {item.item.value for item in expected.items}
    extra_items: list[OrderItem] = [
        item for item in detected.items if item.item.value not in expected_item_names
    ]

    # Validation fails if there are any issues
    is_complete = (
        len(missing_items) == 0
        and len(too_few_items) == 0
        and len(too_many_items) == 0
        and len(extra_items) == 0
    )

    return ComparisonResult(
        is_complete=is_complete,
        missing_items=missing_items,
        too_few_items=too_few_items,
        too_many_items=too_many_items,
        extra_items=extra_items,
        matched_items=matched_items,
    )


__all__ = ["compare_orders"]
