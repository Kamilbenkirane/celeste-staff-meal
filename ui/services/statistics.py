"""Statistics calculation service for validation records."""

from collections import Counter
from datetime import datetime

from staff_meal.models import Item, Statistics, ValidationRecord


def calculate_statistics(records: list[ValidationRecord]) -> Statistics:
    """Calculate statistics from validation records.

    Args:
        records: List of validation records to analyze.

    Returns:
        Statistics object with aggregated data.
    """
    if not records:
        return Statistics(
            total_orders=0,
            complete_orders=0,
            error_rate=0.0,
            most_forgotten_items=[],
            errors_by_hour={},
            errors_by_day={},
        )

    total_orders = len(records)
    complete_orders = sum(1 for r in records if r.is_complete)
    error_rate = ((total_orders - complete_orders) / total_orders * 100) if total_orders > 0 else 0.0

    most_forgotten_items = get_most_forgotten_items(records)
    errors_by_hour = get_errors_by_hour(records)
    errors_by_day = get_errors_by_day(records)

    return Statistics(
        total_orders=total_orders,
        complete_orders=complete_orders,
        error_rate=error_rate,
        most_forgotten_items=most_forgotten_items,
        errors_by_hour=errors_by_hour,
        errors_by_day=errors_by_day,
    )


def get_most_forgotten_items(records: list[ValidationRecord]) -> list[tuple[Item, int]]:
    """Get most frequently forgotten items.

    Args:
        records: List of validation records.

    Returns:
        List of (item, count) tuples sorted by count descending.
    """
    forgotten_items: list[Item] = []
    for record in records:
        if not record.is_complete:
            for mismatch in record.comparison_result.missing_items:
                forgotten_items.append(mismatch.item)

    item_counts = Counter(forgotten_items)
    # Sort by count descending, then by item name for stability
    sorted_items = sorted(item_counts.items(), key=lambda x: (-x[1], x[0].value))

    return [(item, count) for item, count in sorted_items]


def get_errors_by_hour(records: list[ValidationRecord]) -> dict[int, int]:
    """Get error counts grouped by hour of day.

    Args:
        records: List of validation records.

    Returns:
        Dictionary mapping hour (0-23) to error count.
    """
    errors_by_hour: dict[int, int] = {}
    for record in records:
        if not record.is_complete:
            hour = record.timestamp.hour
            errors_by_hour[hour] = errors_by_hour.get(hour, 0) + 1

    # Ensure all hours 0-23 are present with 0 if no errors
    for hour in range(24):
        if hour not in errors_by_hour:
            errors_by_hour[hour] = 0

    return errors_by_hour


def get_errors_by_day(records: list[ValidationRecord]) -> dict[str, int]:
    """Get error counts grouped by day of week.

    Args:
        records: List of validation records.

    Returns:
        Dictionary mapping day name (Monday, Tuesday, etc.) to error count.
    """
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    errors_by_day: dict[str, int] = {}

    for record in records:
        if not record.is_complete:
            day_name = day_names[record.timestamp.weekday()]
            errors_by_day[day_name] = errors_by_day.get(day_name, 0) + 1

    # Ensure all days are present with 0 if no errors
    for day_name in day_names:
        if day_name not in errors_by_day:
            errors_by_day[day_name] = 0

    return errors_by_day


__all__ = ["calculate_statistics", "get_most_forgotten_items", "get_errors_by_hour", "get_errors_by_day"]
