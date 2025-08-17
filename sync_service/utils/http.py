"""HTTP client helpers."""

from __future__ import annotations

import httpx


def create_http_client(timeout: float = 10.0, verify: bool = True) -> httpx.Client:
    """Create a configured httpx.Client."""
    return httpx.Client(timeout=timeout, verify=verify)
