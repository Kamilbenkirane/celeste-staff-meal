"""Tests for database module."""

from unittest.mock import MagicMock, patch

import pytest

import staff_meal.database
from staff_meal.database import (
    get_supabase_client,
    serialize_comparison_result,
    serialize_order,
)
from staff_meal.models import (
    ComparisonResult,
    Item,
    ItemMatch,
    Order,
    OrderItem,
    OrderSource,
)


class TestGetSupabaseClient:
    """Tests for get_supabase_client function."""

    def test_get_supabase_client_success(self) -> None:
        """get_supabase_client returns client when env vars are set."""
        # Reset singleton
        staff_meal.database._supabase_client = None
        mock_client = MagicMock()
        with (
            patch("staff_meal.database.create_client", return_value=mock_client),
            patch(
                "os.getenv",
                side_effect=lambda key, default=None: {
                    "SUPABASE_URL": "https://test.supabase.co",
                    "SUPABASE_KEY": "test-key",
                }.get(key, default),
            ),
        ):
            result = get_supabase_client()

        assert result is mock_client
        # Cleanup
        staff_meal.database._supabase_client = None

    def test_get_supabase_client_success_with_next_public_vars(self) -> None:
        """get_supabase_client works with NEXT_PUBLIC_ prefixed env vars."""
        # Reset singleton
        staff_meal.database._supabase_client = None
        mock_client = MagicMock()
        with (
            patch("staff_meal.database.create_client", return_value=mock_client),
            patch(
                "os.getenv",
                side_effect=lambda key, default=None: {
                    "NEXT_PUBLIC_SUPABASE_URL": "https://test.supabase.co",
                    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "test-key",
                }.get(key, default),
            ),
        ):
            result = get_supabase_client()

        assert result is mock_client
        # Cleanup
        staff_meal.database._supabase_client = None

    def test_get_supabase_client_missing_url_raises_error(self) -> None:
        """get_supabase_client raises ValueError when SUPABASE_URL is missing."""
        # Reset singleton
        staff_meal.database._supabase_client = None
        with (
            patch("os.getenv", return_value=None),
            pytest.raises(ValueError, match="Supabase URL not found"),
        ):
            get_supabase_client()
        # Cleanup
        staff_meal.database._supabase_client = None

    def test_get_supabase_client_missing_key_raises_error(self) -> None:
        """get_supabase_client raises ValueError when SUPABASE_KEY is missing."""
        # Reset singleton
        staff_meal.database._supabase_client = None
        with (
            patch(
                "os.getenv",
                side_effect=lambda key, default=None: {
                    "SUPABASE_URL": "https://test.supabase.co"
                }.get(key, default),
            ),
            pytest.raises(ValueError, match="Supabase key not found"),
        ):
            get_supabase_client()
        # Cleanup
        staff_meal.database._supabase_client = None

    def test_get_supabase_client_singleton_behavior(self) -> None:
        """get_supabase_client returns same instance on subsequent calls."""
        # Reset singleton
        staff_meal.database._supabase_client = None
        mock_client = MagicMock()
        create_client_mock = MagicMock(return_value=mock_client)
        with (
            patch("staff_meal.database.create_client", create_client_mock),
            patch(
                "os.getenv",
                side_effect=lambda key, default=None: {
                    "SUPABASE_URL": "https://test.supabase.co",
                    "SUPABASE_KEY": "test-key",
                }.get(key, default),
            ),
        ):
            client1 = get_supabase_client()
            client2 = get_supabase_client()

        assert client1 is client2
        assert client1 is mock_client
        # create_client should only be called once
        assert create_client_mock.call_count == 1
        # Cleanup
        staff_meal.database._supabase_client = None


class TestSerializeOrder:
    """Tests for serialize_order function."""

    def test_serialize_order_returns_json_string(self) -> None:
        """serialize_order converts Order to JSON string."""
        order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        result = serialize_order(order)

        assert isinstance(result, str)
        assert "ORD-123" in result
        assert "ubereats" in result
        assert "GYOZA" in result or "Gyoza" in result


class TestSerializeComparisonResult:
    """Tests for serialize_comparison_result function."""

    def test_serialize_comparison_result_returns_json_string(self) -> None:
        """serialize_comparison_result converts ComparisonResult to JSON string."""
        comparison_result = ComparisonResult(
            is_complete=True,
            missing_items=[],
            too_few_items=[],
            too_many_items=[],
            extra_items=[],
            matched_items=[
                ItemMatch(
                    item=Item.GYOZA,
                    expected_quantity=2,
                    detected_quantity=2,
                    is_match=True,
                )
            ],
        )

        result = serialize_comparison_result(comparison_result)

        assert isinstance(result, str)
        assert "is_complete" in result
        assert "true" in result.lower() or "True" in result
