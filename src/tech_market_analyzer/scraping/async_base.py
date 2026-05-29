"""Async HTTP base scraper with aiohttp rate limiting."""

import asyncio
import logging
import time

import aiohttp

logger = logging.getLogger(__name__)


class AsyncBaseScraper:
    """Shared async HTTP client with throttling and retries."""

    def __init__(
        self,
        user_agent: str,
        request_delay_seconds: float = 1.5,
        max_concurrency: int = 3,
    ) -> None:
        """Initialize async scraper HTTP settings."""
        self.user_agent = user_agent
        self.request_delay_seconds = request_delay_seconds
        self.max_concurrency = max_concurrency
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._last_request_at: float = 0.0
        self._throttle_lock = asyncio.Lock()

    async def _throttle(self) -> None:
        """Enforce minimum delay between HTTP requests."""
        async with self._throttle_lock:
            elapsed = time.monotonic() - self._last_request_at
            if elapsed < self.request_delay_seconds:
                await asyncio.sleep(self.request_delay_seconds - elapsed)
            self._last_request_at = time.monotonic()

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        """Fetch a page with rate limiting and basic retry."""
        last_error: Exception | None = None
        headers = {"User-Agent": self.user_agent}

        for attempt in range(3):
            async with self._semaphore:
                await self._throttle()
                try:
                    async with session.get(url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.text()
                except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                    last_error = exc
                    logger.warning(
                        "Async request failed (attempt %d): %s", attempt + 1, exc
                    )
                    await asyncio.sleep(2**attempt)

        raise last_error  # type: ignore[misc]
