"""Tests for order validation service."""

from staff_meal.models import (
    ComparisonResult,
    Item,
    Order,
    OrderItem,
    OrderSource,
)
from ui.services.validation import compare_orders


class TestCompareOrders:
    """Tests for compare_orders function."""

    def test_compare_orders_perfect_match(self) -> None:
        """Happy path: all items match exactly."""
        expected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=1),
            ],
        )
        detected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=1),
            ],
        )

        result = compare_orders(expected, detected)

        assert isinstance(result, ComparisonResult)
        assert result.is_complete is True
        assert len(result.missing_items) == 0
        assert len(result.too_few_items) == 0
        assert len(result.too_many_items) == 0
        assert len(result.extra_items) == 0
        assert len(result.matched_items) == 2
        assert all(match.is_match for match in result.matched_items)

    def test_compare_orders_missing_item(self) -> None:
        """Item is missing (not detected at all)."""
        expected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=1),
            ],
        )
        detected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
            ],
        )

        result = compare_orders(expected, detected)

        assert result.is_complete is False
        assert len(result.missing_items) == 1
        assert result.missing_items[0].item == Item.SAUCE
        assert result.missing_items[0].expected_quantity == 1
        assert result.missing_items[0].detected_quantity == 0
        assert len(result.too_few_items) == 0
        assert len(result.too_many_items) == 0

    def test_compare_orders_too_few_items(self) -> None:
        """Item detected but quantity is less than expected."""
        expected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=3),
            ],
        )
        detected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
            ],
        )

        result = compare_orders(expected, detected)

        assert result.is_complete is False
        assert len(result.too_few_items) == 1
        assert result.too_few_items[0].item == Item.GYOZA
        assert result.too_few_items[0].expected_quantity == 3
        assert result.too_few_items[0].detected_quantity == 2
        assert len(result.missing_items) == 0
        assert len(result.too_many_items) == 0

    def test_compare_orders_too_many_items(self) -> None:
        """Item detected but quantity is more than expected."""
        expected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=1),
            ],
        )
        detected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=3),
            ],
        )

        result = compare_orders(expected, detected)

        assert result.is_complete is False
        assert len(result.too_many_items) == 1
        assert result.too_many_items[0].item == Item.GYOZA
        assert result.too_many_items[0].expected_quantity == 1
        assert result.too_many_items[0].detected_quantity == 3
        assert len(result.missing_items) == 0
        assert len(result.too_few_items) == 0

    def test_compare_orders_extra_items(self) -> None:
        """Items detected that are not in expected order."""
        expected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=1),
            ],
        )
        detected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=1),
                OrderItem(item=Item.MAKI_CALIFORNIA, quantity=2),
            ],
        )

        result = compare_orders(expected, detected)

        assert result.is_complete is False
        assert len(result.extra_items) == 1
        assert result.extra_items[0].item == Item.MAKI_CALIFORNIA
        assert result.extra_items[0].quantity == 2
        assert len(result.missing_items) == 0
        assert len(result.too_few_items) == 0
        assert len(result.too_many_items) == 0

    def test_compare_orders_multiple_issues(self) -> None:
        """Multiple issues: missing, too few, too many, and extra items."""
        expected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=3),
                OrderItem(item=Item.SAUCE, quantity=2),
            ],
        )
        detected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=1),  # Too few
                OrderItem(item=Item.MAKI_CALIFORNIA, quantity=1),  # Extra
            ],
        )

        result = compare_orders(expected, detected)

        assert result.is_complete is False
        assert len(result.missing_items) == 1  # SAUCE_SALEE missing
        assert len(result.too_few_items) == 1  # RAVIOLIS too few
        assert len(result.too_many_items) == 0
        assert len(result.extra_items) == 1  # CALIFORNIA_SAUMON extra

    def test_compare_orders_matched_items_includes_all(self) -> None:
        """matched_items includes all expected items with match status."""
        expected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=1),
            ],
        )
        detected = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),  # Match
                OrderItem(item=Item.SAUCE, quantity=0),  # Missing
            ],
        )

        result = compare_orders(expected, detected)

        assert len(result.matched_items) == 2
        raviolis_match = next(m for m in result.matched_items if m.item == Item.GYOZA)
        assert raviolis_match.is_match is True
        assert raviolis_match.expected_quantity == 2
        assert raviolis_match.detected_quantity == 2

        sauce_match = next(m for m in result.matched_items if m.item == Item.SAUCE)
        assert sauce_match.is_match is False
        assert sauce_match.expected_quantity == 1
        assert sauce_match.detected_quantity == 0
