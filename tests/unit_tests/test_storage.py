"""Tests for storage service."""

from datetime import datetime
from pathlib import Path

import pytest

# Note: These tests need to be updated to mock Supabase instead of using local database
# from staff_meal.database import get_db_path, init_database
from staff_meal.models import (
    ComparisonResult,
    Item,
    ItemMismatch,
    Order,
    OrderItem,
    OrderSource,
)
from staff_meal.storage import (
    get_all_validation_records,
    get_validation_history,
    save_validation_result,
)


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Create temporary database for testing."""
    # TODO: Update to mock Supabase client instead
    return tmp_path / "test_validations.db"


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Needs Supabase mocking - TODO: update tests for Supabase integration"
)
async def test_save_validation_result(temp_db: Path) -> None:
    """Test saving validation result to database."""
    # await init_database()

    expected_order = Order(
        order_id="ORD-123",
        source=OrderSource.UBER_EATS,
        items=[
            OrderItem(item=Item.MAKI_CALIFORNIA, quantity=2),
            OrderItem(item=Item.SAUCE, quantity=1),
        ],
    )

    detected_order = Order(
        order_id="ORD-123",
        source=OrderSource.UBER_EATS,
        items=[
            OrderItem(item=Item.MAKI_CALIFORNIA, quantity=2),
            OrderItem(item=Item.SAUCE, quantity=1),
        ],
    )

    comparison_result = ComparisonResult(
        is_complete=True,
        missing_items=[],
        too_few_items=[],
        too_many_items=[],
        extra_items=[],
        matched_items=[],
    )

    await save_validation_result(
        expected_order=expected_order,
        detected_order=detected_order,
        comparison_result=comparison_result,
        operator="test_operator",
    )

    # Verify record was saved
    records = await get_validation_history(limit=10)
    assert len(records) == 1
    assert records[0].order_id == "ORD-123"
    assert records[0].is_complete is True
    assert records[0].operator == "test_operator"


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Needs Supabase mocking - TODO: update tests for Supabase integration"
)
async def test_get_validation_history(temp_db: Path) -> None:
    """Test retrieving validation history."""
    # await init_database()

    # Save multiple records
    for i in range(5):
        order = Order(
            order_id=f"ORD-{i}",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=1)],
        )
        comparison_result = ComparisonResult(
            is_complete=i % 2 == 0,  # Alternate complete/incomplete
            missing_items=[],
            too_few_items=[],
            too_many_items=[],
            extra_items=[],
            matched_items=[],
        )
        await save_validation_result(
            expected_order=order,
            detected_order=order,
            comparison_result=comparison_result,
        )

    # Retrieve history
    records = await get_validation_history(limit=10)
    assert len(records) == 5

    # Test limit
    records_limited = await get_validation_history(limit=3)
    assert len(records_limited) == 3


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Needs Supabase mocking - TODO: update tests for Supabase integration"
)
async def test_get_validation_history_with_date_filter(temp_db: Path) -> None:
    """Test retrieving validation history with date filters."""
    # await init_database()

    # Save a record
    order = Order(
        order_id="ORD-123",
        source=OrderSource.UBER_EATS,
        items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=1)],
    )
    comparison_result = ComparisonResult(
        is_complete=True,
        missing_items=[],
        too_few_items=[],
        too_many_items=[],
        extra_items=[],
        matched_items=[],
    )
    await save_validation_result(
        expected_order=order,
        detected_order=order,
        comparison_result=comparison_result,
    )

    # Test with date filters
    start_date = datetime.now()
    records = await get_validation_history(start_date=start_date, limit=10)
    assert len(records) >= 1

    # Test with future date (should return empty)
    future_date = datetime(2099, 1, 1)
    records_future = await get_validation_history(start_date=future_date, limit=10)
    assert len(records_future) == 0


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Needs Supabase mocking - TODO: update tests for Supabase integration"
)
async def test_get_all_validation_records(temp_db: Path) -> None:
    """Test getting all validation records."""
    # await init_database()

    # Save multiple records
    for i in range(10):
        order = Order(
            order_id=f"ORD-{i}",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=1)],
        )
        comparison_result = ComparisonResult(
            is_complete=True,
            missing_items=[],
            too_few_items=[],
            too_many_items=[],
            extra_items=[],
            matched_items=[],
        )
        await save_validation_result(
            expected_order=order,
            detected_order=order,
            comparison_result=comparison_result,
        )

    records = await get_all_validation_records()
    assert len(records) == 10


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Needs Supabase mocking - TODO: update tests for Supabase integration"
)
async def test_save_validation_result_with_missing_items(temp_db: Path) -> None:
    """Test saving validation result with missing items."""
    # await init_database()

    expected_order = Order(
        order_id="ORD-123",
        source=OrderSource.UBER_EATS,
        items=[
            OrderItem(item=Item.MAKI_CALIFORNIA, quantity=2),
            OrderItem(item=Item.SAUCE, quantity=1),
        ],
    )

    detected_order = Order(
        order_id="ORD-123",
        source=OrderSource.UBER_EATS,
        items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=2)],
    )

    comparison_result = ComparisonResult(
        is_complete=False,
        missing_items=[
            ItemMismatch(item=Item.SAUCE, expected_quantity=1, detected_quantity=0),
        ],
        too_few_items=[],
        too_many_items=[],
        extra_items=[],
        matched_items=[],
    )

    await save_validation_result(
        expected_order=expected_order,
        detected_order=detected_order,
        comparison_result=comparison_result,
    )

    # Verify record was saved with missing items
    records = await get_validation_history(limit=1)
    assert len(records) == 1
    assert records[0].is_complete is False
    assert len(records[0].comparison_result.missing_items) == 1
    assert records[0].comparison_result.missing_items[0].item == Item.SAUCE
