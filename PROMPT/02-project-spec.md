# 02-project-spec

## Purpose
A stateless FastAPI service that periodically syncs Active Directory group membership into Open WebUI user groups using the OWUI admin API. Identity is matched by email. Users not yet present in OWUI are skipped with INFO log. Deletes only remove users from the corresponding OWUI group.

## Configuration
- Reads `config/config.yaml` once on startup; values come from env vars.
- `.env.example` provides defaults for local dev.
- Supports multiple services via adapters; initial target is Open WebUI.
- Sync interval default 60s; retries and backoff configurable.

## Behavior
1. On startup load config and optionally resolve OWUI group IDs.
2. Each sync iteration processes mappings sequentially:
   - Fetch LDAP group members and emails.
   - Fetch OWUI group members.
   - Compute adds/deletes and reconcile via OWUI API.
   - Skip users missing from OWUI `/api/v1/users`.
3. Transient errors use bounded retries; failures log and skip iteration.

## Observability
- Structured JSON logging with fields for counts, adds, deletes, duration, errors.
- Prometheus metrics: counters (`sync_iterations_total`, `sync_errors_total{target,kind}`, `owui_add_total`, `owui_delete_total`, `ldap_lookup_errors_total`, `owui_http_errors_total`), histograms (`sync_iteration_seconds`, `external_request_seconds{target}`), gauges (`last_sync_timestamp_seconds`, `inflight_requests{target}`).

## FastAPI Surface
Endpoints: `/healthz`, `/readyz`, `/metrics`, `/version`.

## Tests
Unit tests for config parsing, diff logic, and OpenWebUI client behavior. Integration tests via docker-compose.
