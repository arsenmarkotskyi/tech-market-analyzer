"""Tests for async HTTP helpers."""

import ssl

from tech_market_analyzer.scraping.async_base import make_aiohttp_ssl_context


def test_make_aiohttp_ssl_context_is_verifying_context():
    context = make_aiohttp_ssl_context()
    assert isinstance(context, ssl.SSLContext)
    assert context.verify_mode == ssl.CERT_REQUIRED
