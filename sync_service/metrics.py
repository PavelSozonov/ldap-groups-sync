"""Prometheus metrics registry and helpers."""

from __future__ import annotations

from contextlib import contextmanager
import time

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
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

sync_errors_total = Counter(
    "sync_errors_total",
    "Total sync errors",
    labelnames=("target", "kind"),
    registry=registry,
)

owui_add_total = Counter(
    "owui_add_total",
    "Total users added to OpenWebUI groups",
    registry=registry,
)

owui_delete_total = Counter(
    "owui_delete_total",
    "Total users removed from OpenWebUI groups",
    registry=registry,
)

ldap_lookup_errors_total = Counter(
    "ldap_lookup_errors_total",
    "Total LDAP lookup errors",
    registry=registry,
)

owui_http_errors_total = Counter(
    "owui_http_errors_total",
    "Total OpenWebUI HTTP errors",
    registry=registry,
)

external_request_seconds = Histogram(
    "external_request_seconds",
    "Duration of external requests",
    labelnames=("target",),
    registry=registry,
)

inflight_requests = Gauge(
    "inflight_requests",
    "Number of inflight external requests",
    labelnames=("target",),
    registry=registry,
)


def export_metrics() -> bytes:
    return generate_latest(registry)


@contextmanager
def track_external_request(target: str):
    """Context manager to record external request metrics."""
    inflight_requests.labels(target=target).inc()
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        external_request_seconds.labels(target=target).observe(duration)
        inflight_requests.labels(target=target).dec()
