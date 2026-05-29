"""Base scraper with rate limiting and HTTP retry logic."""

import logging
import time
from abc import ABC

import httpx

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Shared HTTP client setup and request throttling for scrapers."""

    def __init__(
        self,
        base_url: str,
        user_agent: str,
        request_delay_seconds: float = 1.5,
        max_pages: int = 10,
    ) -> None:
        """Initialize base scraper configuration.

        Parameters
        ----------
        base_url : str
            Root URL of the job board.
        user_agent : str
            HTTP User-Agent header value.
        request_delay_seconds : float
            Delay between consecutive requests.
        max_pages : int
            Maximum number of listing pages to scrape.
        """
        self.base_url = base_url.rstrip("/")
        self.request_delay_seconds = request_delay_seconds
        self.max_pages = max_pages
        self._last_request_at: float = 0.0
        self._client = httpx.Client(
            headers={"User-Agent": user_agent},
            timeout=30.0,
            follow_redirects=True,
        )

    def _throttle(self) -> None:
        """Enforce minimum delay between HTTP requests."""
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.request_delay_seconds:
            time.sleep(self.request_delay_seconds - elapsed)
        self._last_request_at = time.monotonic()

    def fetch_page(self, url: str) -> str:
        """Fetch a page with rate limiting and basic retry.

        Parameters
        ----------
        url : str
            Full URL to fetch.

        Returns
        -------
        str
            Response body as text.

        Raises
        ------
        httpx.HTTPStatusError
            If the server returns an error after retries.
        """
        last_error: Exception | None = None
        for attempt in range(3):
            self._throttle()
            try:
                response = self._client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning("Request failed (attempt %d): %s", attempt + 1, exc)
                time.sleep(2**attempt)
        raise last_error  # type: ignore[misc]

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "BaseScraper":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
