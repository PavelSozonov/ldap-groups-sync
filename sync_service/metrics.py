"""Prometheus metrics registry and helpers."""

from __future__ import annotations

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
)

registry = CollectorRegistry()

sync_iterations_total = Counter(
    "sync_iterations_total",
    "Total sync iterations",
    registry=registry,
)

sync_iteration_seconds = Histogram(
    "sync_iteration_seconds",
    "Sync iteration duration in seconds",
    registry=registry,
)

last_sync_timestamp_seconds = Gauge(
    "last_sync_timestamp_seconds",
    "Timestamp of last sync",
    registry=registry,
)


def export_metrics() -> bytes:
    return generate_latest(registry)
