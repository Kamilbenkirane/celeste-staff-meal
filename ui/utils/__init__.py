"""Utility functions and classes for Celeste Staff Meal UI."""

import asyncio
import threading
from typing import Any

from celeste.core import Provider
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


def get_provider_favicon_url(provider: Provider) -> str:
    """Get favicon URL for a provider.

    Uses direct favicon URLs where available, falls back to Google's favicon service.

    Args:
        provider: Provider enum value.

        Returns:
            Favicon URL string.
    """
    provider_urls: dict[Provider, str] = {
        Provider.GOOGLE: "https://www.google.com/favicon.ico",
        Provider.OPENAI: "https://www.openai.com/favicon.ico",
        Provider.ANTHROPIC: "https://www.anthropic.com/favicon.ico",
        Provider.MISTRAL: "https://mistral.ai/favicon.ico",
        Provider.COHERE: "https://cohere.com/favicon.ico",
        Provider.XAI: "https://x.ai/favicon.ico",
    }

    if provider in provider_urls:
        return provider_urls[provider]

    domain_map: dict[Provider, str] = {
        Provider.PERPLEXITY: "perplexity.ai",
        Provider.HUGGINGFACE: "huggingface.co",
        Provider.REPLICATE: "replicate.com",
        Provider.STABILITYAI: "stability.ai",
        Provider.LUMA: "lumalabs.ai",
        Provider.TOPAZLABS: "topazlabs.com",
        Provider.BYTEDANCE: "byteplus.com",
    }

    domain = domain_map.get(provider, f"{provider.value}.com")
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=32"


runner = AsyncRunner()

__all__ = ["AsyncRunner", "get_provider_favicon_url", "runner", "pil_image_to_bytes"]
