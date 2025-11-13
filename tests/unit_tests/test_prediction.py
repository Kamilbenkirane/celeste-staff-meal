"""Tests for order prediction service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from staff_meal.models import Item, Order, OrderItem, OrderSource
from ui.services.prediction import predict_order, predict_order_async


class TestPredictOrderAsync:
    """Tests for predict_order_async function."""

    @pytest.mark.asyncio
    async def test_predict_order_async_success(self) -> None:
        """Happy path: successfully predict order from bag image."""
        bag_image = Image.new("RGB", (100, 100), color="white")
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=1)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=1),
            ],
        )

        mock_output = MagicMock()
        mock_output.content = detected_order

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.prediction.create_client", return_value=mock_client):
            result = await predict_order_async(bag_image, expected_order=expected_order)

        assert result.order_id == expected_order.order_id
        assert result.source == expected_order.source
        assert len(result.items) == 2
        assert any(
            item.item == Item.GYOZA and item.quantity == 2 for item in result.items
        )
        assert any(
            item.item == Item.SAUCE and item.quantity == 1 for item in result.items
        )

    @pytest.mark.asyncio
    async def test_predict_order_async_no_expected_order(self) -> None:
        """predict_order_async works without expected_order."""
        bag_image = Image.new("RGB", (100, 100), color="white")

        detected_order = Order(
            order_id="ORD-456",
            source=OrderSource.DELIVEROO,
            items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=1)],
        )

        mock_output = MagicMock()
        mock_output.content = detected_order

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.prediction.create_client", return_value=mock_client):
            result = await predict_order_async(bag_image)

        assert result.order_id == detected_order.order_id
        assert result.source == detected_order.source
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_predict_order_async_filters_zero_quantities(self) -> None:
        """predict_order_async filters out items with quantity <= 0."""
        bag_image = Image.new("RGB", (100, 100), color="white")

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=0),  # Should be filtered
                OrderItem(item=Item.MAKI_CALIFORNIA, quantity=-1),  # Should be filtered
            ],
        )

        mock_output = MagicMock()
        mock_output.content = detected_order

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.prediction.create_client", return_value=mock_client):
            result = await predict_order_async(bag_image)

        assert len(result.items) == 1
        assert result.items[0].item == Item.GYOZA
        assert result.items[0].quantity == 2

    @pytest.mark.asyncio
    async def test_predict_order_async_no_valid_items_raises_error(self) -> None:
        """predict_order_async raises ValueError when no valid items detected."""
        bag_image = Image.new("RGB", (100, 100), color="white")

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=0),  # Invalid
            ],
        )

        mock_output = MagicMock()
        mock_output.content = detected_order

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with (
            patch("ui.services.prediction.create_client", return_value=mock_client),
            pytest.raises(ValueError, match="No valid items detected"),
        ):
            await predict_order_async(bag_image)

    @pytest.mark.asyncio
    async def test_predict_order_async_none_image_raises_error(self) -> None:
        """predict_order_async raises ValueError when bag_image is None."""
        with pytest.raises(ValueError, match="Bag image cannot be None"):
            await predict_order_async(None)  # type: ignore[arg-type]


class TestPredictOrder:
    """Tests for predict_order function (synchronous wrapper)."""

    @patch("ui.utils.runner")
    def test_predict_order_calls_async_version(self, mock_runner: MagicMock) -> None:
        """predict_order calls predict_order_async via runner."""
        bag_image = Image.new("RGB", (100, 100), color="white")
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=1)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_runner.run.return_value = detected_order

        result = predict_order(bag_image, expected_order=expected_order)

        assert result == detected_order
        mock_runner.run.assert_called_once()
