"""Staff Meal - Meal order verification platform for restaurants.

A platform to verify meal orders before bagging to prevent missing items,
reduce complaints, and improve ratings on delivery platforms like UberEats and Deliveroo.
"""

from staff_meal.models import (
    ComparisonResult,
    Item,
    ItemMatch,
    ItemMismatch,
    Order,
    OrderItem,
    OrderSource,
    Statistics,
    ValidationRecord,
)
from staff_meal.order_storage import get_all_orders, save_order
from staff_meal.qr import decode_qr, generate_qr
from staff_meal.storage import (
    get_all_validation_records,
    get_validation_history,
    save_validation_result,
)

__version__ = "0.1.0"

__all__: list[str] = [
    "ComparisonResult",
    "Item",
    "ItemMatch",
    "ItemMismatch",
    "Order",
    "OrderItem",
    "OrderSource",
    "Statistics",
    "ValidationRecord",
    "decode_qr",
    "generate_qr",
    "get_all_orders",
    "get_all_validation_records",
    "get_validation_history",
    "save_order",
    "save_validation_result",
]
