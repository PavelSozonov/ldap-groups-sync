# 03-acceptance-checklist

- `.env` completed; OWUI API reachable.
- `config/config.yaml` loads once; identity via email; AD group schema matches.
- LDAP: bind, search groups, resolve members; retries/timeouts.
- OWUI: Bearer auth, resolve group IDs, add/remove users, skip missing users.
- Reconciliation: set-diff adds/deletes only for groups.
- Scheduling: periodic loop with graceful shutdown.
- Clients: explicit timeouts, bounded retry with jitter.
- Observability: JSON logs, Prometheus metrics.
- Stateless: each iteration recomputes.
- Demo stack: Bitnami OpenLDAP + Open WebUI.
- Tests: unit tests and integration tests pass.
