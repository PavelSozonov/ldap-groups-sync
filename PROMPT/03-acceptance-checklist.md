# 03-acceptance-checklist

- `.env` completed; target service APIs reachable.
- `config/config.yaml` loads once; identity via email; AD group schema matches.
- LDAP: bind, search groups, resolve members; retries/timeouts.
- Target services: Bearer auth, resolve group IDs, add/remove users, skip missing users.
- Multi-engine: parallel execution, independent configuration, no interference.
- Reconciliation: set-diff adds/deletes only for groups.
- Scheduling: periodic loops with graceful shutdown.
- Clients: explicit timeouts, bounded retry with jitter.
- Observability: JSON logs, Prometheus metrics, engine status endpoint.
- Stateless: each iteration recomputes.
- Demo stack: Bitnami OpenLDAP + Open WebUI + Mock API.
- Tests: unit tests and integration tests pass.
