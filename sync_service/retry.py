"""Retry helpers using tenacity."""

from __future__ import annotations

from tenacity import retry, stop_after_attempt, wait_random_exponential


def retry_on_exception(retries: int, base: float = 0.5, max_backoff: float = 10.0):
    return retry(
        stop=stop_after_attempt(retries),
        wait=wait_random_exponential(multiplier=base, max=max_backoff),
    )
