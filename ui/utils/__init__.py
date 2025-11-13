"""Utility functions and classes for Celeste Staff Meal UI."""

import asyncio
import threading
from typing import Any

from ui.utils.image import pil_image_to_bytes


class AsyncRunner:
    """Dedicated thread with persistent event loop for async operations.

    Solves the "bound to different event loop" issue by ensuring all async
    operations run in a single persistent event loop in a background thread.
    This allows HTTPClient singletons with connection pooling to work correctly.
    """

    def __init__(self) -> None:
        """Initialize runner and start background event loop."""
        self.loop: asyncio.AbstractEventLoop | None = None
        self._start_loop()

    def _start_loop(self) -> None:
        """Start event loop in background thread."""

        def run_loop() -> None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()

        # Wait for loop initialization
        while self.loop is None:
            pass

    def run(self, coro: Any) -> Any:  # noqa: ANN401
        """Submit coroutine to background loop and return result.

        Args:
            coro: Coroutine to execute in background loop.

        Returns:
            Result from coroutine execution.
        """
        if self.loop is None:
            msg = "Event loop not initialized"
            raise RuntimeError(msg)
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()


# Global runner - single persistent event loop for all async operations
runner = AsyncRunner()

__all__ = ["AsyncRunner", "runner", "pil_image_to_bytes"]
