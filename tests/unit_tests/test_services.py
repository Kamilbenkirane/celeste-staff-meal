"""Tests for UI service layer."""

from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from staff_meal.models import Item, Order, OrderItem, OrderSource
from ui.services import read_qr_order


class TestReadQROrder:
    """Tests for read_qr_order function."""

    @patch("ui.services.decode_qr")
    def test_read_qr_order_with_pil_image(self, mock_decode_qr: MagicMock) -> None:
        """read_qr_order works with PIL Image."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=1)],
        )
        mock_decode_qr.return_value = expected_order

        # Create a dummy PIL Image
        qr_image = Image.new("RGB", (100, 100), color="white")

        result = read_qr_order(qr_image)

        assert result == expected_order
        mock_decode_qr.assert_called_once()

    @patch("ui.services.decode_qr")
    @patch("PIL.Image.open")
    def test_read_qr_order_with_bytes(
        self, mock_image_open: MagicMock, mock_decode_qr: MagicMock
    ) -> None:
        """read_qr_order works with bytes."""
        expected_order = Order(
            order_id="ORD-456",
            source=OrderSource.DELIVEROO,
            items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=2)],
        )
        mock_decode_qr.return_value = expected_order

        # Create a mock PIL Image
        mock_image = Image.new("RGB", (100, 100), color="white")
        mock_image_open.return_value = mock_image

        # Create dummy bytes
        qr_bytes = b"fake image bytes"

        result = read_qr_order(qr_bytes)

        assert result == expected_order
        mock_decode_qr.assert_called_once()

    def test_read_qr_order_none_raises_error(self) -> None:
        """read_qr_order raises ValueError when qr_image is None."""
        with pytest.raises(ValueError, match="QR code non reconnu"):
            read_qr_order(None)

    @patch("ui.services.decode_qr")
    def test_read_qr_order_decode_error_raises_value_error(
        self, mock_decode_qr: MagicMock
    ) -> None:
        """read_qr_order raises ValueError when decode_qr fails."""
        mock_decode_qr.side_effect = ValueError("No QR code found")

        qr_image = Image.new("RGB", (100, 100), color="white")

        with pytest.raises(ValueError, match="QR code non reconnu"):
            read_qr_order(qr_image)

    @patch("ui.services.decode_qr")
    def test_read_qr_order_key_error_raises_value_error(
        self, mock_decode_qr: MagicMock
    ) -> None:
        """read_qr_order raises ValueError when decode_qr raises KeyError."""
        mock_decode_qr.side_effect = KeyError("missing_key")

        qr_image = Image.new("RGB", (100, 100), color="white")

        with pytest.raises(ValueError, match="QR code non reconnu"):
            read_qr_order(qr_image)

    @patch("ui.services.decode_qr")
    def test_read_qr_order_type_error_raises_value_error(
        self, mock_decode_qr: MagicMock
    ) -> None:
        """read_qr_order raises ValueError when decode_qr raises TypeError."""
        mock_decode_qr.side_effect = TypeError("invalid type")

        qr_image = Image.new("RGB", (100, 100), color="white")

        with pytest.raises(ValueError, match="QR code non reconnu"):
            read_qr_order(qr_image)
