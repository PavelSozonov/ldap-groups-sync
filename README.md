# ldap-groups-sync

A stateless FastAPI service that syncs LDAP group membership into Open WebUI groups.

```
+-----------+       +----------------+
|   LDAP    | ----> | Open WebUI API |
+-----------+       +----------------+
```

## Quick Start

```bash
docker compose up --build
```

The service exposes `/healthz`, `/readyz`, `/metrics`, and `/version` on port 8000.

## License

[MIT](LICENSE)
