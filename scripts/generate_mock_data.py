"""Script to generate mock validation records for testing dashboard."""

import asyncio
import random  # nosec B311
from datetime import datetime, timedelta
from typing import Optional

import json

from staff_meal.database import get_supabase_client, serialize_comparison_result, serialize_order
from staff_meal.models import (
    ComparisonResult,
    Item,
    ItemMatch,
    ItemMismatch,
    Order,
    OrderItem,
    OrderSource,
)
from ui.services.validation import compare_orders


def generate_random_order(
    order_id: str,
    source: OrderSource,
    num_items: int = 3,
) -> Order:
    """Generate a random order with specified number of items.

    Args:
        order_id: Order identifier.
        source: Order source platform.
        num_items: Number of items in the order.

    Returns:
        Generated Order object.
    """
    all_items = list(Item)
    selected_items = random.sample(all_items, min(num_items, len(all_items)))

    items = [
        OrderItem(item=item, quantity=random.randint(1, 3)) for item in selected_items
    ]

    return Order(order_id=order_id, source=source, items=items)


def create_complete_order(order_id: str, source: OrderSource) -> tuple[Order, Order]:
    """Create a complete order (no errors).

    Args:
        order_id: Order identifier.
        source: Order source platform.

    Returns:
        Tuple of (expected_order, detected_order) that match perfectly.
    """
    expected = generate_random_order(order_id, source)
    detected = Order(
        order_id=order_id,
        source=source,
        items=[OrderItem(item=item.item, quantity=item.quantity) for item in expected.items],
    )
    return expected, detected


def create_missing_items_order(
    order_id: str,
    source: OrderSource,
) -> tuple[Order, Order]:
    """Create an order with missing items.

    Args:
        order_id: Order identifier.
        source: Order source platform.

    Returns:
        Tuple of (expected_order, detected_order) with missing items.
    """
    expected = generate_random_order(order_id, source, num_items=4)
    # Remove 1-2 items randomly
    num_to_remove = random.randint(1, min(2, len(expected.items)))
    items_to_keep = random.sample(expected.items, len(expected.items) - num_to_remove)
    detected = Order(
        order_id=order_id,
        source=source,
        items=[OrderItem(item=item.item, quantity=item.quantity) for item in items_to_keep],
    )
    return expected, detected


def create_too_few_items_order(
    order_id: str,
    source: OrderSource,
) -> tuple[Order, Order]:
    """Create an order with too few items (quantities less than expected).

    Args:
        order_id: Order identifier.
        source: Order source platform.

    Returns:
        Tuple of (expected_order, detected_order) with too few items.
    """
    expected = generate_random_order(order_id, source, num_items=3)
    detected_items = []
    for item in expected.items:
        if random.random() < 0.5:  # 50% chance to reduce quantity
            detected_qty = max(1, item.quantity - random.randint(1, item.quantity))
            detected_items.append(OrderItem(item=item.item, quantity=detected_qty))
        else:
            detected_items.append(OrderItem(item=item.item, quantity=item.quantity))

    detected = Order(order_id=order_id, source=source, items=detected_items)
    return expected, detected


def create_too_many_items_order(
    order_id: str,
    source: OrderSource,
) -> tuple[Order, Order]:
    """Create an order with too many items (quantities more than expected).

    Args:
        order_id: Order identifier.
        source: Order source platform.

    Returns:
        Tuple of (expected_order, detected_order) with too many items.
    """
    expected = generate_random_order(order_id, source, num_items=3)
    detected_items = []
    for item in expected.items:
        if random.random() < 0.4:  # 40% chance to increase quantity
            detected_qty = item.quantity + random.randint(1, 2)
            detected_items.append(OrderItem(item=item.item, quantity=detected_qty))
        else:
            detected_items.append(OrderItem(item=item.item, quantity=item.quantity))

    detected = Order(order_id=order_id, source=source, items=detected_items)
    return expected, detected


def create_extra_items_order(
    order_id: str,
    source: OrderSource,
) -> tuple[Order, Order]:
    """Create an order with extra items (items not in expected order).

    Args:
        order_id: Order identifier.
        source: Order source platform.

    Returns:
        Tuple of (expected_order, detected_order) with extra items.
    """
    expected = generate_random_order(order_id, source, num_items=3)
    detected = Order(
        order_id=order_id,
        source=source,
        items=[OrderItem(item=item.item, quantity=item.quantity) for item in expected.items],
    )

    # Add 1-2 extra items
    all_items = list(Item)
    expected_item_names = {item.item.value for item in expected.items}
    available_extra = [item for item in all_items if item.value not in expected_item_names]
    if available_extra:
        num_extra = random.randint(1, min(2, len(available_extra)))
        extra_items = random.sample(available_extra, num_extra)
        for extra_item in extra_items:
            detected.items.append(OrderItem(item=extra_item, quantity=random.randint(1, 2)))

    return expected, detected


def create_combined_errors_order(
    order_id: str,
    source: OrderSource,
) -> tuple[Order, Order]:
    """Create an order with multiple types of errors.

    Args:
        order_id: Order identifier.
        source: Order source platform.

    Returns:
        Tuple of (expected_order, detected_order) with combined errors.
    """
    expected = generate_random_order(order_id, source, num_items=4)
    detected_items = []

    # Keep some items, remove some, modify quantities
    for item in expected.items:
        rand = random.random()
        if rand < 0.3:  # 30% chance to remove
            continue
        elif rand < 0.6:  # 30% chance to modify quantity
            detected_qty = max(1, item.quantity + random.randint(-1, 1))
            detected_items.append(OrderItem(item=item.item, quantity=detected_qty))
        else:  # 40% chance to keep as is
            detected_items.append(OrderItem(item=item.item, quantity=item.quantity))

    # Add extra items sometimes
    if random.random() < 0.5:
        all_items = list(Item)
        expected_item_names = {item.item.value for item in expected.items}
        available_extra = [item for item in all_items if item.value not in expected_item_names]
        if available_extra:
            extra_item = random.choice(available_extra)
            detected_items.append(OrderItem(item=extra_item, quantity=1))

    detected = Order(order_id=order_id, source=source, items=detected_items)
    return expected, detected


async def generate_mock_records(
    num_records: int = 100,
    days_back: int = 90,
    operators: Optional[list[str]] = None,
) -> None:
    """Generate mock validation records and save to database.

    Args:
        num_records: Number of records to generate.
        days_back: Number of days back to distribute records (default: 90 days = 3 months).
        operators: Optional list of operator names. If None, uses default operators.
    """
    if operators is None:
        operators = ["Alice", "Bob", "Charlie", "Diana", "Eve"]

    sources = [OrderSource.UBER_EATS, OrderSource.DELIVEROO]

    # Error scenario generators with weights
    error_scenarios = [
        (create_complete_order, 75),  # 75% complete orders
        (create_missing_items_order, 12),  # 12% missing items
        (create_too_few_items_order, 6),  # 6% too few
        (create_too_many_items_order, 3),  # 3% too many
        (create_extra_items_order, 2),  # 2% extra items
        (create_combined_errors_order, 2),  # 2% combined errors
    ]

    # Create weighted list
    weighted_scenarios: list[tuple] = []
    for scenario_func, weight in error_scenarios:
        weighted_scenarios.extend([scenario_func] * weight)

    start_date = datetime.now() - timedelta(days=days_back)
    supabase = get_supabase_client()

    print(f"Generating {num_records} mock validation records...")
    print(f"Date range: {start_date.date()} to {datetime.now().date()} ({days_back} days)")

    for i in range(num_records):
        # Random timestamp within date range - distribute evenly across the period
        days_offset = random.uniform(0, days_back)
        hours_offset = random.uniform(8, 22)  # Business hours 8 AM to 10 PM
        minutes_offset = random.randint(0, 59)
        timestamp = start_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)

        # Random order ID
        order_id = f"MOCK-{random.randint(1000, 9999)}-{i:04d}"

        # Random source
        source = random.choice(sources)

        # Random operator
        operator = random.choice(operators)

        # Select scenario based on weights
        scenario_func = random.choice(weighted_scenarios)
        expected, detected = scenario_func(order_id, source)

        # Compare orders to get comparison result
        comparison_result = compare_orders(expected, detected)

        # Save to database with custom timestamp
        data = {
            "order_id": expected.order_id,
            "timestamp": timestamp.isoformat(),
            "operator": operator,
            "is_complete": comparison_result.is_complete,
            "expected_order_json": json.loads(serialize_order(expected)),
            "detected_order_json": json.loads(serialize_order(detected)),
            "comparison_result_json": json.loads(serialize_comparison_result(comparison_result)),
        }

        # Insert into Supabase
        supabase.table("validation_records").insert(data).execute()

        if (i + 1) % 10 == 0:
            print(f"Generated {i + 1}/{num_records} records...")

    print(f"✅ Successfully generated {num_records} mock validation records!")


def main() -> None:
    """Main entry point for CLI."""
    import sys

    # Parse command line arguments
    num_records = 100
    days = 30

    if len(sys.argv) > 1:
        num_records = int(sys.argv[1])
    if len(sys.argv) > 2:
        days = int(sys.argv[2])

    asyncio.run(generate_mock_records(num_records=num_records, days_back=days))


if __name__ == "__main__":
    main()
