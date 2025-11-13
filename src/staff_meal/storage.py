"""Database service layer for saving and querying validation records using Supabase."""

import json
from datetime import datetime
from typing import Any, cast

from staff_meal.database import (
    get_supabase_client,
    serialize_comparison_result,
    serialize_order,
)
from staff_meal.models import ComparisonResult, Order, OrderItem, ValidationRecord


async def save_validation_result(
    expected_order: Order,
    detected_order: Order,
    comparison_result: ComparisonResult,
    operator: str | None = None,
) -> None:
    """Save validation result to Supabase database.

    Args:
        expected_order: Expected order from QR code.
        detected_order: Detected order from bag image.
        comparison_result: Result of comparison.
        operator: Optional operator identifier.
    """
    supabase = get_supabase_client()

    # Prepare data for insertion
    data = {
        "order_id": expected_order.order_id,
        "timestamp": datetime.now().isoformat(),
        "operator": operator,
        "is_complete": comparison_result.is_complete,
        "expected_order_json": json.loads(serialize_order(expected_order)),
        "detected_order_json": json.loads(serialize_order(detected_order)),
        "comparison_result_json": json.loads(
            serialize_comparison_result(comparison_result)
        ),
    }

    # Insert into Supabase
    supabase.table("validation_records").insert(data).execute()


async def get_validation_history(
    limit: int = 100,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[ValidationRecord]:
    """Get validation history from Supabase database.

    Args:
        limit: Maximum number of records to return.
        start_date: Optional start date filter.
        end_date: Optional end date filter.

    Returns:
        List of ValidationRecord objects.
    """
    supabase = get_supabase_client()

    # Build query
    query = supabase.table("validation_records").select("*")

    # Apply date filters
    if start_date:
        query = query.gte("timestamp", start_date.isoformat())

    if end_date:
        query = query.lte("timestamp", end_date.isoformat())

    # Order by timestamp descending and limit
    query = query.order("timestamp", desc=True).limit(limit)

    # Execute query
    response = query.execute()

    # Convert response to ValidationRecord objects
    records: list[ValidationRecord] = []
    for row_data in response.data:
        # Type assertion: Supabase returns dict[str, Any] for each row
        row = cast(dict[str, Any], row_data)

        # Parse JSON fields back to models
        expected_order_dict = cast(dict[str, Any], row["expected_order_json"])
        detected_order_dict = cast(dict[str, Any], row["detected_order_json"])
        comparison_result_dict = cast(dict[str, Any], row["comparison_result_json"])

        # Convert to Pydantic models
        expected_order = Order.model_validate(expected_order_dict)
        detected_order = Order.model_validate(detected_order_dict)
        comparison_result = ComparisonResult.model_validate(comparison_result_dict)

        # Handle extra_items which might be dicts instead of OrderItem objects
        if "extra_items" in comparison_result_dict:
            extra_items_data = comparison_result_dict["extra_items"]
            if isinstance(extra_items_data, list):
                extra_items = []
                for item_dict in extra_items_data:
                    extra_items.append(
                        OrderItem.model_validate(cast(dict[str, Any], item_dict))
                    )
                comparison_result.extra_items = extra_items

        # Parse timestamp
        timestamp_str = row["timestamp"]
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = cast(datetime, timestamp_str)

        record = ValidationRecord(
            id=cast(int | None, row["id"]),
            order_id=cast(str, row["order_id"]),
            timestamp=timestamp,
            operator=cast(str | None, row.get("operator")),
            is_complete=bool(row["is_complete"]),
            expected_order=expected_order,
            detected_order=detected_order,
            comparison_result=comparison_result,
        )
        records.append(record)

    return records


async def get_all_validation_records(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[ValidationRecord]:
    """Get all validation records (no limit).

    Args:
        start_date: Optional start date filter.
        end_date: Optional end date filter.

    Returns:
        List of all ValidationRecord objects matching filters.
    """
    # Use a large limit for "all" records
    return await get_validation_history(
        limit=1000000, start_date=start_date, end_date=end_date
    )


__all__ = [
    "get_all_validation_records",
    "get_validation_history",
    "save_validation_result",
]
