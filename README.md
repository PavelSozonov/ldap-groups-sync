# LDAP Groups Sync

A stateless FastAPI service that periodically syncs LDAP group membership into multiple target services (OpenWebUI, mock services, etc.) using their respective admin APIs. Identity is matched by email. Users not yet present in target services are skipped with INFO log. The service supports multiple engines running in parallel, each with its own configuration and sync intervals.

## Quick Start

### 1. Start All Services

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps
```

### 2. Automatic Setup

The system automatically:
- Generates API keys for target services
- Updates configuration with real API keys
- Starts multiple sync engines with correct settings

### 3. Verify Operation

```bash
# Check sync service metrics
curl http://localhost:8000/metrics

# Check health endpoints
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

## Manual Setup (if needed)

If automatic setup doesn't work, follow these steps:

### 1. Open target services in browser
```
OpenWebUI: http://localhost:8080
```

### 2. Create admin accounts
- **OpenWebUI**: Email `admin@example.com`, Password `adminpassword`

### 3. Create API keys
1. Go to **Settings > Account** in each service
2. Create new API key
3. Copy the key

### 4. Update configuration
```bash
# Save API keys to files
echo "YOUR_API_KEY_HERE" > .owui_api_key

# Update configuration
python3 scripts/update_config.py
```

## Configuration

### Environment Variables (.env)

```bash
# LDAP Configuration
LDAP_URL=ldap://openldap:1389
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=adminpassword
LDAP_VERIFY_TLS=false
VERIFY_TLS=false

# OpenWebUI Configuration
OWUI_BASE_URL=http://openwebui:8080
OWUI_ADMIN_EMAIL=admin@example.com
OWUI_ADMIN_PASSWORD=adminpassword
OWUI_ADMIN_NAME=Admin User
```

### Service Configuration (config/config.yaml)

```yaml
services:
- name: owui
  type: openwebui
  base_url: http://openwebui:8080
  group_mappings:
    - ldap_group_dn: "cn=dep1,ou=groups,dc=example,dc=com"
      target_group_name: "Demo Group A"
    - ldap_group_dn: "cn=dep2,ou=groups,dc=example,dc=com"
      target_group_name: "Demo Group B"
  sync:
    interval_seconds: 60
    retries: 3
```

## Monitoring

### Prometheus Metrics

```bash
# Get all metrics
curl http://localhost:8000/metrics

# Key metrics:
# - sync_iterations_total - number of sync iterations
# - external_request_seconds - external service request duration
# - owui_http_errors_total - OpenWebUI HTTP errors
# - ldap_lookup_errors_total - LDAP lookup errors
# - owui_add_total - users added to OpenWebUI groups
# - owui_delete_total - users removed from OpenWebUI groups
```

### Health Checks

```bash
# Readiness check
curl http://localhost:8000/readyz

# Health check
curl http://localhost:8000/healthz
```

## Architecture

### Services

1. **OpenLDAP** - source of user and group data
2. **OpenWebUI** - primary target system for synchronization
3. **Mock API** - test API for development and validation
4. **Sync Service** - main synchronization service with multi-engine support

### Components

- **LDAP Provider** - LDAP connection
- **Service Adapters** - API interaction for different target services
- **Engine Manager** - manages multiple sync engines
- **Sync Engines** - individual synchronization logic per service
- **Metrics** - Prometheus metrics

## Testing

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/
```

### Test Data

Demo data is automatically loaded into OpenLDAP:
- User: `demo@example.com`
- Groups: `dep1`, `dep2`

## Debugging

### Service Logs

```bash
# Sync service logs
docker compose logs sync

# OpenWebUI logs
docker compose logs openwebui

# OpenLDAP logs
docker compose logs openldap
```

### Connection Verification

```bash
# Check LDAP
docker compose exec sync ldapsearch -H ldap://openldap:1389 -D "cn=admin,dc=example,dc=com" -w adminpassword -b "dc=example,dc=com"

# Check OpenWebUI API
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8080/api/v1/groups
```

## Development

### Project Structure

```
├── sync_service/          # Main code
│   ├── adapters/         # External service adapters
│   ├── domain/           # Domain models
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── scripts/              # Setup scripts
├── config/               # Configuration
├── tests/                # Tests
├── ldif/                 # LDAP data files
└── compose.yaml          # Docker Compose
```

### Adding New Service

1. Create adapter in `sync_service/adapters/`
2. Add adapter to factory in `sync_service/adapters/factory.py`
3. Add service configuration in `config/config.yaml`
4. Add tests

## Troubleshooting

### Service Issues

1. **Target service not responding**
   ```bash
   # Check status
   docker compose ps
   
   # Check logs
   docker compose logs
   ```

2. **API key not working**
   ```bash
   # Regenerate key
   python3 scripts/generate_api_key.py
   
   # Update configuration
   python3 scripts/update_config.py
   ```

3. **Engine not starting**
   ```bash
   # Check engine status
   curl http://localhost:8000/engines/status
   
   # Check sync service logs
   docker compose logs sync
   ```

### LDAP Issues

1. **Cannot connect to LDAP**
   ```bash
   # Check environment variables
   cat .env
   
   # Test connection
   docker compose exec sync ldapsearch -H ldap://openldap:1389 -D "cn=admin,dc=example,dc=com" -w adminpassword -b "dc=example,dc=com"
   ```

### Synchronization Issues

1. **Sync service not starting**
   ```bash
   # Check logs
   docker compose logs sync
   
   # Check configuration
   cat config/config.yaml
   ```

## Integration Testing

The project includes comprehensive integration testing with multiple target services:

1. **Real OpenWebUI API** - Tests against actual OpenWebUI endpoints
2. **Mock API** - Tests against mock service for validation
3. **LDAP Integration** - Real LDAP server with demo data
4. **Multi-Engine Sync** - Parallel synchronization to multiple services
5. **End-to-End Sync** - Complete synchronization workflow
6. **Metrics Validation** - Prometheus metrics verification

### Test Results

**Successfully tested:**
- LDAP user and group discovery
- OpenWebUI API authentication
- Mock service integration
- Group membership synchronization
- User addition to groups
- User removal from groups (via group update)
- Multi-engine parallel operation
- Metrics collection and monitoring
- Full bidirectional synchronization

## License

MIT License
