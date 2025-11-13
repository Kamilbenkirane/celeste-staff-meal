"""Tests for storage service."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from staff_meal.database import serialize_comparison_result, serialize_order
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


def _create_mock_validation_record(
    order_id: str,
    record_id: int = 1,
    operator: str | None = None,
    is_complete: bool = True,
    timestamp: str | None = None,
    comparison_result: ComparisonResult | None = None,
) -> dict:
    """Create a mock validation record dict for Supabase response."""
    order = Order(
        order_id=order_id,
        source=OrderSource.UBER_EATS,
        items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=1)],
    )

    if comparison_result is None:
        comparison_result = ComparisonResult(
            is_complete=is_complete,
            missing_items=[],
            too_few_items=[],
            too_many_items=[],
            extra_items=[],
            matched_items=[],
        )

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    return {
        "id": record_id,
        "order_id": order_id,
        "timestamp": timestamp,
        "operator": operator,
        "is_complete": is_complete,
        "expected_order_json": json.loads(serialize_order(order)),
        "detected_order_json": json.loads(serialize_order(order)),
        "comparison_result_json": json.loads(
            serialize_comparison_result(comparison_result)
        ),
    }


class TestSaveValidationResult:
    """Tests for save_validation_result function."""

    @pytest.mark.asyncio
    async def test_save_validation_result_saves_to_supabase(self) -> None:
        """save_validation_result saves validation record with all fields."""
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

        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        mock_insert.execute = mock_execute
        mock_table.insert.return_value = mock_insert

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            await save_validation_result(
                expected_order=expected_order,
                detected_order=detected_order,
                comparison_result=comparison_result,
                operator="test_operator",
            )

        mock_client.table.assert_called_once_with("validation_records")
        mock_table.insert.assert_called_once()
        call_args = mock_table.insert.call_args[0][0]
        assert call_args["order_id"] == "ORD-123"
        assert call_args["operator"] == "test_operator"
        assert call_args["is_complete"] is True
        assert "expected_order_json" in call_args
        assert "detected_order_json" in call_args
        assert "comparison_result_json" in call_args
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_validation_result_without_operator(self) -> None:
        """save_validation_result saves record without operator."""
        order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=1)],
        )

        comparison_result = ComparisonResult(
            is_complete=True,
            missing_items=[],
            too_few_items=[],
            too_many_items=[],
            extra_items=[],
            matched_items=[],
        )

        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        mock_insert.execute = mock_execute
        mock_table.insert.return_value = mock_insert

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            await save_validation_result(
                expected_order=order,
                detected_order=order,
                comparison_result=comparison_result,
            )

        call_args = mock_table.insert.call_args[0][0]
        assert call_args["operator"] is None


class TestGetValidationHistory:
    """Tests for get_validation_history function."""

    @pytest.mark.asyncio
    async def test_get_validation_history_retrieves_records(self) -> None:
        """get_validation_history retrieves records with limit."""
        mock_response = MagicMock()
        mock_response.data = [
            _create_mock_validation_record("ORD-1", record_id=1, is_complete=True),
            _create_mock_validation_record("ORD-2", record_id=2, is_complete=False),
        ]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_select = MagicMock()
        mock_select.order.return_value = mock_order
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(limit=10)

        assert len(result) == 2
        assert result[0].order_id == "ORD-1"
        assert result[0].is_complete is True
        assert result[1].order_id == "ORD-2"
        assert result[1].is_complete is False
        mock_order.limit.assert_called_once_with(10)

    @pytest.mark.asyncio
    async def test_get_validation_history_with_start_date(self) -> None:
        """get_validation_history filters by start_date."""
        start_date = datetime(2024, 1, 1)
        mock_response = MagicMock()
        mock_response.data = [
            _create_mock_validation_record("ORD-1", timestamp="2024-01-15T10:00:00"),
        ]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_gte = MagicMock()
        mock_gte.order.return_value = mock_order
        mock_select = MagicMock()
        mock_select.gte.return_value = mock_gte
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(start_date=start_date, limit=10)

        mock_select.gte.assert_called_once_with("timestamp", start_date.isoformat())
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_validation_history_with_end_date(self) -> None:
        """get_validation_history filters by end_date."""
        end_date = datetime(2024, 12, 31)
        mock_response = MagicMock()
        mock_response.data = [
            _create_mock_validation_record("ORD-1", timestamp="2024-06-15T10:00:00"),
        ]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_lte = MagicMock()
        mock_lte.order.return_value = mock_order
        mock_select = MagicMock()
        mock_select.lte.return_value = mock_lte
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(end_date=end_date, limit=10)

        mock_select.lte.assert_called_once_with("timestamp", end_date.isoformat())
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_validation_history_with_both_dates(self) -> None:
        """get_validation_history filters by both start_date and end_date."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        mock_response = MagicMock()
        mock_response.data = [
            _create_mock_validation_record("ORD-1", timestamp="2024-06-15T10:00:00"),
        ]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_lte = MagicMock()
        mock_lte.order.return_value = mock_order
        mock_gte = MagicMock()
        mock_gte.lte.return_value = mock_lte
        mock_select = MagicMock()
        mock_select.gte.return_value = mock_gte
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(
                start_date=start_date, end_date=end_date, limit=10
            )

        mock_select.gte.assert_called_once_with("timestamp", start_date.isoformat())
        mock_gte.lte.assert_called_once_with("timestamp", end_date.isoformat())
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_validation_history_with_extra_items(self) -> None:
        """get_validation_history handles extra_items in comparison_result."""
        comparison_result = ComparisonResult(
            is_complete=False,
            missing_items=[],
            too_few_items=[],
            too_many_items=[],
            extra_items=[OrderItem(item=Item.GYOZA, quantity=1)],
            matched_items=[],
        )

        mock_record = _create_mock_validation_record(
            "ORD-1", comparison_result=comparison_result
        )
        mock_response = MagicMock()
        mock_response.data = [mock_record]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_select = MagicMock()
        mock_select.order.return_value = mock_order
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(limit=10)

        assert len(result) == 1
        assert len(result[0].comparison_result.extra_items) == 1
        assert result[0].comparison_result.extra_items[0].item == Item.GYOZA

    @pytest.mark.asyncio
    async def test_get_validation_history_timestamp_parsing(self) -> None:
        """get_validation_history parses timestamp strings correctly."""
        # Test with Z suffix
        mock_response = MagicMock()
        mock_response.data = [
            _create_mock_validation_record("ORD-1", timestamp="2024-01-15T10:00:00Z"),
        ]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_select = MagicMock()
        mock_select.order.return_value = mock_order
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(limit=10)

        assert len(result) == 1
        assert isinstance(result[0].timestamp, datetime)

    @pytest.mark.asyncio
    async def test_get_validation_history_timestamp_already_datetime(self) -> None:
        """get_validation_history handles timestamp that is already datetime."""
        timestamp_dt = datetime(2024, 1, 15, 10, 0, 0)
        mock_record = _create_mock_validation_record(
            "ORD-1", timestamp="2024-01-15T10:00:00"
        )
        # Override timestamp to be datetime object
        mock_record["timestamp"] = timestamp_dt

        mock_response = MagicMock()
        mock_response.data = [mock_record]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_select = MagicMock()
        mock_select.order.return_value = mock_order
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(limit=10)

        assert len(result) == 1
        assert result[0].timestamp == timestamp_dt

    @pytest.mark.asyncio
    async def test_get_validation_history_without_extra_items_key(self) -> None:
        """get_validation_history handles comparison_result without extra_items key."""
        comparison_result = ComparisonResult(
            is_complete=True,
            missing_items=[],
            too_few_items=[],
            too_many_items=[],
            extra_items=[],
            matched_items=[],
        )

        mock_record = _create_mock_validation_record(
            "ORD-1", comparison_result=comparison_result
        )
        # Remove extra_items key to test the branch where it's not in dict
        del mock_record["comparison_result_json"]["extra_items"]

        mock_response = MagicMock()
        mock_response.data = [mock_record]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_select = MagicMock()
        mock_select.order.return_value = mock_order
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(limit=10)

        assert len(result) == 1
        # extra_items should remain empty since key was missing
        assert len(result[0].comparison_result.extra_items) == 0

    @pytest.mark.asyncio
    async def test_get_validation_history_empty_result(self) -> None:
        """get_validation_history handles empty results."""
        mock_response = MagicMock()
        mock_response.data = []

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_select = MagicMock()
        mock_select.order.return_value = mock_order
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_validation_history(limit=10)

        assert len(result) == 0
        assert result == []


class TestGetAllValidationRecords:
    """Tests for get_all_validation_records function."""

    @pytest.mark.asyncio
    async def test_get_all_validation_records_calls_get_validation_history(
        self,
    ) -> None:
        """get_all_validation_records calls get_validation_history with large limit."""
        mock_response = MagicMock()
        mock_response.data = [
            _create_mock_validation_record(f"ORD-{i}", record_id=i) for i in range(10)
        ]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_select = MagicMock()
        mock_select.order.return_value = mock_order
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_all_validation_records()

        assert len(result) == 10
        # Verify it used the large limit
        mock_order.limit.assert_called_once_with(1000000)

    @pytest.mark.asyncio
    async def test_get_all_validation_records_with_date_filters(self) -> None:
        """get_all_validation_records passes date filters to get_validation_history."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        mock_response = MagicMock()
        mock_response.data = [
            _create_mock_validation_record("ORD-1", timestamp="2024-06-15T10:00:00"),
        ]

        mock_limit = MagicMock()
        mock_limit.execute.return_value = mock_response
        mock_order = MagicMock()
        mock_order.limit.return_value = mock_limit
        mock_lte = MagicMock()
        mock_lte.order.return_value = mock_order
        mock_gte = MagicMock()
        mock_gte.lte.return_value = mock_lte
        mock_select = MagicMock()
        mock_select.gte.return_value = mock_gte
        mock_table = MagicMock()
        mock_table.select.return_value = mock_select

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            result = await get_all_validation_records(
                start_date=start_date, end_date=end_date
            )

        assert len(result) == 1
        mock_select.gte.assert_called_once_with("timestamp", start_date.isoformat())
        mock_gte.lte.assert_called_once_with("timestamp", end_date.isoformat())


class TestSaveValidationResultWithMissingItems:
    """Tests for save_validation_result with missing items."""

    @pytest.mark.asyncio
    async def test_save_validation_result_with_missing_items(self) -> None:
        """save_validation_result saves record with missing items correctly."""
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

        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        mock_insert.execute = mock_execute
        mock_table.insert.return_value = mock_insert

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch("staff_meal.storage.get_supabase_client", return_value=mock_client):
            await save_validation_result(
                expected_order=expected_order,
                detected_order=detected_order,
                comparison_result=comparison_result,
            )

        call_args = mock_table.insert.call_args[0][0]
        assert call_args["is_complete"] is False
        # Verify comparison_result_json contains missing_items
        comparison_json = call_args["comparison_result_json"]
        assert len(comparison_json["missing_items"]) == 1
        assert comparison_json["missing_items"][0]["item"] == Item.SAUCE.value
