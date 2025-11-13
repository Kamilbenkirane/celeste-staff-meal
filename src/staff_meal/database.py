"""Supabase client initialization and connection management for validation records."""

import os

from dotenv import load_dotenv

from staff_meal.models import ComparisonResult, Order
from supabase import Client, create_client

# Load environment variables
load_dotenv()

# Singleton client instance
_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance.

    Returns:
        Supabase client instance.

    Raises:
        ValueError: If Supabase credentials are not configured via environment variables.
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    # Try multiple environment variable names for compatibility
    supabase_url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv(
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    )

    if not supabase_url:
        msg = (
            "Supabase URL not found. Please set SUPABASE_URL or NEXT_PUBLIC_SUPABASE_URL "
            "environment variable."
        )
        raise ValueError(msg)

    if not supabase_key:
        msg = (
            "Supabase key not found. Please set SUPABASE_KEY or NEXT_PUBLIC_SUPABASE_ANON_KEY "
            "environment variable."
        )
        raise ValueError(msg)

    _supabase_client = create_client(supabase_url, supabase_key)
    return _supabase_client


def serialize_order(order: Order) -> str:
    """Serialize Order to JSON string.

    Args:
        order: Order to serialize.

    Returns:
        JSON string representation.
    """
    return order.model_dump_json()


def serialize_comparison_result(result: ComparisonResult) -> str:
    """Serialize ComparisonResult to JSON string.

    Args:
        result: ComparisonResult to serialize.

    Returns:
        JSON string representation.
    """
    return result.model_dump_json()


__all__ = ["get_supabase_client", "serialize_comparison_result", "serialize_order"]
