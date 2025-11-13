"""Tests for domain models."""

import pytest
from pydantic import ValidationError

from staff_meal.models import Item, Order, OrderItem, OrderSource


class TestOrderItem:
    """Tests for OrderItem model."""

    def test_create_valid_order_item(self) -> None:
        """Happy path: valid OrderItem creation."""
        order_item = OrderItem(item=Item.GYOZA, quantity=2)
        assert order_item.item == Item.GYOZA
        assert order_item.quantity == 2

    def test_order_item_str_representation(self) -> None:
        """OrderItem string representation formats correctly."""
        order_item = OrderItem(item=Item.MAKI_CALIFORNIA, quantity=3)
        assert str(order_item) == "3x Boite de 6 California Rolls"

    def test_order_item_quantity_can_be_zero_or_negative(self) -> None:
        """OrderItem quantity accepts any integer (validation happens in application logic)."""
        # Note: We removed gt=0 constraint to fix JSON schema compatibility.
        # Invalid quantities are filtered in application logic (e.g., predict_order).
        order_item_zero = OrderItem(item=Item.GYOZA, quantity=0)
        assert order_item_zero.quantity == 0

        order_item_negative = OrderItem(item=Item.GYOZA, quantity=-1)
        assert order_item_negative.quantity == -1

    def test_order_item_quantity_must_be_integer(self) -> None:
        """OrderItem quantity validation: must be an integer type."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItem(item=Item.GYOZA, quantity=2.5)  # type: ignore[arg-type]
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("quantity",) for error in errors)

    def test_order_item_requires_item_field(self) -> None:
        """OrderItem validation: item field is required."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItem(quantity=1)  # type: ignore[call-arg]
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("item",) for error in errors)


class TestOrder:
    """Tests for Order model."""

    def test_create_valid_order(self) -> None:
        """Happy path: valid Order creation."""
        order_item = OrderItem(item=Item.GYOZA, quantity=2)
        order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[order_item],
        )
        assert order.order_id == "ORD-123"
        assert order.source == OrderSource.UBER_EATS
        assert len(order.items) == 1
        assert order.items[0] == order_item

    def test_order_total_items_single_item(self) -> None:
        """Order.total_items() correctly sums single item quantity."""
        order_item = OrderItem(item=Item.GYOZA, quantity=5)
        order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[order_item],
        )
        assert order.total_items() == 5

    def test_order_total_items_multiple_items(self) -> None:
        """Order.total_items() correctly sums multiple item quantities."""
        items = [
            OrderItem(item=Item.GYOZA, quantity=2),
            OrderItem(item=Item.MAKI_CALIFORNIA, quantity=3),
            OrderItem(item=Item.SAUCE, quantity=1),
        ]
        order = Order(
            order_id="ORD-123",
            source=OrderSource.DELIVEROO,
            items=items,
        )
        assert order.total_items() == 6

    def test_order_items_must_not_be_empty(self) -> None:
        """Order validation: items list must have at least one item."""
        with pytest.raises(ValidationError) as exc_info:
            Order(
                order_id="ORD-123",
                source=OrderSource.UBER_EATS,
                items=[],
            )
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("items",) and "at least 1" in str(error["msg"]).lower()
            for error in errors
        )

    @pytest.mark.parametrize(
        "missing_field,kwargs",
        [
            (
                "order_id",
                {
                    "source": OrderSource.UBER_EATS,
                    "items": [OrderItem(item=Item.GYOZA, quantity=1)],
                },
            ),
            (
                "source",
                {
                    "order_id": "ORD-123",
                    "items": [OrderItem(item=Item.GYOZA, quantity=1)],
                },
            ),
            (
                "items",
                {
                    "order_id": "ORD-123",
                    "source": OrderSource.UBER_EATS,
                },
            ),
        ],
    )
    def test_order_requires_all_fields(self, missing_field: str, kwargs: dict) -> None:
        """Order validation: all required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            Order(**kwargs)
        errors = exc_info.value.errors()
        assert any(error["loc"] == (missing_field,) for error in errors)
