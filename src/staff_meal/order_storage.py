"""Order storage service for saving orders to Supabase."""

from typing import Any, cast

from staff_meal.database import get_supabase_client
from staff_meal.models import Item, Order, OrderItem, OrderSource


async def save_order(order: Order) -> None:
    """Save order to Supabase database.

    Args:
        order: Order object to save.
    """
    supabase = get_supabase_client()

    # Convert order items to dict format for JSONB storage
    items_data = [
        {"item": item.item.value, "quantity": item.quantity} for item in order.items
    ]

    # Prepare data for insertion
    data = {
        "order_id": order.order_id,
        "source": order.source.value,
        "items_json": items_data,
    }

    # Insert into Supabase
    supabase.table("orders").insert(data).execute()


async def get_all_orders(limit: int = 100) -> list[Order]:
    """Get all saved orders from Supabase database.

    Args:
        limit: Maximum number of orders to return.

    Returns:
        List of Order objects, ordered by created_at DESC.
    """
    supabase = get_supabase_client()

    # Query orders table, ordered by created_at descending
    response = (
        supabase.table("orders")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    # Convert response to Order objects
    orders: list[Order] = []
    for row_data in response.data:
        # Type assertion: Supabase returns dict[str, Any] for each row
        row = cast(dict[str, Any], row_data)

        # Parse items_json back to OrderItem objects
        items_data = cast(list[dict[str, Any]], row["items_json"])
        order_items = [
            OrderItem(
                item=Item(cast(str, item_data["item"])),
                quantity=cast(int, item_data["quantity"]),
            )
            for item_data in items_data
        ]

        # Create Order object
        order = Order(
            order_id=cast(str, row["order_id"]),
            source=OrderSource(cast(str, row["source"])),
            items=order_items,
        )
        orders.append(order)

    return orders


__all__ = ["get_all_orders", "save_order"]
