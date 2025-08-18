# 02-project-spec

## Purpose
A stateless FastAPI service that periodically syncs Active Directory group membership into multiple target services (Open WebUI, mock services, etc.) using their respective admin APIs. Identity is matched by email. Users not yet present in target services are skipped with INFO log. The service supports multiple engines running in parallel, each with its own configuration and sync intervals.

## Configuration
- Reads `config/config.yaml` once on startup; values come from env vars.
- `.env.example` provides defaults for local dev.
- Supports multiple services via adapters; each service has its own configuration.
- Each service defines its own sync interval, retries, and backoff settings.

## Behavior
1. On startup load config and build engines for all configured services.
2. Each engine runs independently with its own sync interval:
   - Fetch LDAP group members and emails.
   - Fetch target service group members.
   - Compute adds/deletes and reconcile via target service API.
   - Skip users missing from target service.
3. Transient errors use bounded retries; failures log and skip iteration.
4. Multiple engines run in parallel without interference.

## Observability
- Structured JSON logging with fields for counts, adds, deletes, duration, errors.
- Prometheus metrics: counters (`sync_iterations_total`, `sync_errors_total{target,kind}`, `owui_add_total`, `owui_delete_total`, `ldap_lookup_errors_total`, `owui_http_errors_total`), histograms (`sync_iteration_seconds`, `external_request_seconds{target}`), gauges (`last_sync_timestamp_seconds`, `inflight_requests{target}`).

## FastAPI Surface
Endpoints: `/healthz`, `/readyz`, `/metrics`, `/version`, `/engines/status`.

## Tests
Unit tests for config parsing, diff logic, and service adapter behavior. Integration tests via docker-compose with multiple target services.
