"""Tests for order storage service."""

from unittest.mock import MagicMock, patch

import pytest

from staff_meal.models import Item, Order, OrderItem, OrderSource
from staff_meal.order_storage import get_all_orders, save_order


class TestSaveOrder:
    """Tests for save_order function."""

    @pytest.mark.asyncio
    async def test_save_order_saves_to_supabase(self) -> None:
        """save_order saves order to Supabase with correct data structure."""
        order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=1),
            ],
        )

        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        mock_insert.execute = mock_execute
        mock_table.insert.return_value = mock_insert

        mock_client = MagicMock()
        mock_client.table.return_value = mock_table

        with patch(
            "staff_meal.order_storage.get_supabase_client", return_value=mock_client
        ):
            await save_order(order)

        # Verify table was called with "orders"
        mock_client.table.assert_called_once_with("orders")
        # Verify insert was called
        mock_table.insert.assert_called_once()
        # Verify data structure
        call_args = mock_table.insert.call_args[0][0]
        assert call_args["order_id"] == "ORD-123"
        assert call_args["source"] == "ubereats"
        assert len(call_args["items_json"]) == 2
        assert call_args["items_json"][0]["item"] == Item.GYOZA.value
        assert call_args["items_json"][0]["quantity"] == 2
        assert call_args["items_json"][1]["item"] == Item.SAUCE.value
        assert call_args["items_json"][1]["quantity"] == 1
        # Verify execute was called
        mock_execute.assert_called_once()


class TestGetAllOrders:
    """Tests for get_all_orders function."""

    @pytest.mark.asyncio
    async def test_get_all_orders_retrieves_from_supabase(self) -> None:
        """get_all_orders retrieves orders from Supabase and converts to Order objects."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "order_id": "ORD-123",
                "source": "ubereats",
                "items_json": [
                    {"item": Item.GYOZA.value, "quantity": 2},
                    {"item": Item.SAUCE.value, "quantity": 1},
                ],
            },
            {
                "order_id": "ORD-456",
                "source": "deliveroo",
                "items_json": [{"item": Item.MAKI_CALIFORNIA.value, "quantity": 1}],
            },
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

        with patch(
            "staff_meal.order_storage.get_supabase_client", return_value=mock_client
        ):
            result = await get_all_orders(limit=100)

        # Verify table was called with "orders"
        mock_client.table.assert_called_once_with("orders")
        # Verify select was called
        mock_table.select.assert_called_once_with("*")
        # Verify order was called with correct parameters
        mock_select.order.assert_called_once_with("created_at", desc=True)
        # Verify limit was called
        mock_order.limit.assert_called_once_with(100)
        # Verify results
        assert len(result) == 2
        assert result[0].order_id == "ORD-123"
        assert result[0].source == OrderSource.UBER_EATS
        assert len(result[0].items) == 2
        assert result[0].items[0].item == Item.GYOZA
        assert result[0].items[0].quantity == 2
        assert result[1].order_id == "ORD-456"
        assert result[1].source == OrderSource.DELIVEROO

    @pytest.mark.asyncio
    async def test_get_all_orders_with_limit(self) -> None:
        """get_all_orders respects limit parameter."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "order_id": "ORD-123",
                "source": "ubereats",
                "items_json": [{"item": Item.GYOZA.value, "quantity": 1}],
            }
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

        with patch(
            "staff_meal.order_storage.get_supabase_client", return_value=mock_client
        ):
            result = await get_all_orders(limit=5)

        mock_order.limit.assert_called_once_with(5)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_all_orders_empty_result(self) -> None:
        """get_all_orders handles empty results from Supabase."""
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

        with patch(
            "staff_meal.order_storage.get_supabase_client", return_value=mock_client
        ):
            result = await get_all_orders()

        assert len(result) == 0
        assert result == []
