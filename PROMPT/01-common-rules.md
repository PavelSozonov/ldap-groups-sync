# 01-common-rules

## Common Engineering Rules

- Python 3.12; dependencies pinned in requirements.txt.
- Enforce PEP 8; format with black; lint with ruff. Full PEP 484 type hints and docstrings.
- Architecture with domain, adapters, app separation.
- No global mutable state; use dependency injection. Small, testable units.
- Input/config validation with Pydantic v2.
- Logging structured JSON by default (`LOG_FORMAT=json`), optional human-readable console for local dev.
- Include UTC timestamps, level, event name, correlation/request IDs. Never log secrets.
- Prometheus metrics: expose `/metrics`; instrument counters, histograms, and gauges for critical paths. Expose `/healthz` and `/readyz`.
- Use modern HTTP client with explicit timeouts everywhere. Implement bounded retries with exponential backoff and jitter.
- For directory/LDAP clients: robust bind/search, schema-aware filters, paging; configurable timeouts and retries.
- Idempotent external operations where possible.
- Graceful shutdown on SIGTERM/SIGINT.
- Secrets only via env; never in repo or logs.
- TLS verification configurable for test vs. prod; clearly document risks.
- Containers run as non-root, minimal layers; healthcheck defined in K8s manifests, not Dockerfile.
- Docker Compose for local dev; K8s-ready logging.
- pytest for unit tests (no external network); compose-based integration tests for dependent services.
- Professional README; MIT LICENSE at root.
- Keep prompts/specs in `PROMPT/` as source of truth.
- Do not use emojis in code, comments, documentation, or commit messages. Use plain text only.
