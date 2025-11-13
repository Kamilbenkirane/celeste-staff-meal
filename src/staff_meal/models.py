"""Domain models for meal order verification."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Item(str, Enum):
    """Predefined menu items for this restaurant."""

    # Note: Values reflect actual packaging units (boxes, containers, etc.)
    # Simplified for MVP - avoid variants that are visually similar

    # Sushi Rolls (Maki) - Boxes of 6 pieces
    MAKI_CALIFORNIA = "Boite de 6 California Rolls"
    MAKI = "Boite de 6 Maki"  # Generic - covers saumon, thon, etc.

    # Sashimi - Boxes with piece count
    SASHIMI_SAUMON = "Boite de 6 Sashimi Saumon"
    SASHIMI_THON = "Boite de 6 Sashimi Thon"

    # Gyoza - Boxes of 4 pieces
    GYOZA = "Boite de 4 Gyoza"

    # Yakitori - Individual skewers
    YAKITORI_BOEUF_FROMAGE = "Yakitori Boeuf Fromage x2"
    YAKITORI_BOULETTE = "Yakitori Boulette"

    # Soups - Individual containers
    SOUPE_MISO = "Soupe Miso"
    RAMEN = "Ramen"

    # Salads - Individual containers
    SALADE_WAKAME = "Salade Wakame"

    # Bowls - Individual containers
    BOWL_SAUMON = "Bowl Saumon Teriyaki"

    # Sauces - Individual packets/containers (generic)
    SAUCE = "Sauce"  # Generic - covers soja, teriyaki, etc.

    # Desserts
    MOCHI = "Boite de 2 Mochi"


class OrderSource(str, Enum):
    """Order source platform."""

    UBER_EATS = "ubereats"
    DELIVEROO = "deliveroo"


class OrderItem(BaseModel):
    """An item expected in the order."""

    item: Item = Field(..., description="Menu item")
    quantity: int = Field(..., description="Quantity")

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.quantity}x {self.item.value}"


class Order(BaseModel):
    """Complete order from QR code."""

    order_id: str = Field(..., description="Unique order identifier")
    source: OrderSource = Field(..., description="Order source platform")
    items: list[OrderItem] = Field(..., min_length=1, description="Items in the order")

    def total_items(self) -> int:
        """Total quantity of all items."""
        return sum(item.quantity for item in self.items)


class ItemMismatch(BaseModel):
    """Item quantity mismatch information."""

    item: Item = Field(..., description="Menu item")
    expected_quantity: int = Field(..., description="Expected quantity")
    detected_quantity: int = Field(..., description="Detected quantity")


class ItemMatch(BaseModel):
    """Item match information."""

    item: Item = Field(..., description="Menu item")
    expected_quantity: int = Field(..., description="Expected quantity")
    detected_quantity: int = Field(..., description="Detected quantity")
    is_match: bool = Field(..., description="Whether quantities match")


class ComparisonResult(BaseModel):
    """Result of comparing expected and detected orders."""

    is_complete: bool = Field(
        ..., description="True if all items match and no extra items"
    )
    missing_items: list[ItemMismatch] = Field(
        default_factory=list, description="Items not detected at all"
    )
    too_few_items: list[ItemMismatch] = Field(
        default_factory=list, description="Items with detected < expected"
    )
    too_many_items: list[ItemMismatch] = Field(
        default_factory=list, description="Items with detected > expected"
    )
    extra_items: list[OrderItem] = Field(
        default_factory=list, description="Items detected but not expected"
    )
    matched_items: list[ItemMatch] = Field(
        default_factory=list, description="All items with match status"
    )


class ValidationRecord(BaseModel):
    """Record of a validation result stored in the database."""

    id: int | None = Field(None, description="Database record ID")
    order_id: str = Field(..., description="Order identifier")
    timestamp: datetime = Field(..., description="Validation timestamp")
    operator: str | None = Field(None, description="Operator who performed validation")
    is_complete: bool = Field(..., description="Whether validation passed")
    expected_order: Order = Field(..., description="Expected order")
    detected_order: Order = Field(..., description="Detected order")
    comparison_result: ComparisonResult = Field(..., description="Comparison result")


class Statistics(BaseModel):
    """Aggregated statistics from validation records."""

    total_orders: int = Field(..., description="Total number of orders validated")
    complete_orders: int = Field(..., description="Number of complete orders")
    error_rate: float = Field(..., description="Error rate as percentage (0-100)")
    most_forgotten_items: list[tuple[Item, int]] = Field(
        default_factory=list,
        description="List of (item, count) tuples for most forgotten items",
    )
    errors_by_hour: dict[int, int] = Field(
        default_factory=dict,
        description="Dictionary mapping hour (0-23) to error count",
    )
    errors_by_day: dict[str, int] = Field(
        default_factory=dict, description="Dictionary mapping day name to error count"
    )
