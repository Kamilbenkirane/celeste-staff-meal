"""Script to delete mock validation records from database."""

import asyncio

from staff_meal.database import get_supabase_client


async def delete_mock_records() -> int:
    """Delete all validation records with order_id starting with 'MOCK-'.

    Returns:
        Number of records deleted.
    """
    supabase = get_supabase_client()

    # First, get all mock records to count them
    response = supabase.table("validation_records").select("id", count="exact").like("order_id", "MOCK-%").execute()

    count = response.count if hasattr(response, "count") and response.count is not None else 0

    if count == 0:
        print("No mock records found to delete.")
        return 0

    print(f"Found {count} mock records to delete...")

    # Delete all mock records
    # Note: Supabase doesn't support LIKE in delete directly, so we need to delete in batches
    # We'll use ilike for case-insensitive matching
    deleted_count = 0
    batch_size = 1000

    while True:
        # Get a batch of IDs to delete
        batch_response = (
            supabase.table("validation_records")
            .select("id")
            .like("order_id", "MOCK-%")
            .limit(batch_size)
            .execute()
        )

        if not batch_response.data or len(batch_response.data) == 0:
            break

        # Extract IDs
        ids_to_delete = [row["id"] for row in batch_response.data if "id" in row]

        if not ids_to_delete:
            break

        # Delete this batch
        for record_id in ids_to_delete:
            supabase.table("validation_records").delete().eq("id", record_id).execute()
            deleted_count += 1

        print(f"Deleted {deleted_count}/{count} records...")

    print(f"✅ Successfully deleted {deleted_count} mock validation records!")
    return deleted_count


def main() -> None:
    """Main entry point for CLI."""
    asyncio.run(delete_mock_records())


if __name__ == "__main__":
    main()
