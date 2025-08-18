# LDAP Groups Sync

A stateless FastAPI service that periodically syncs LDAP group membership into OpenWebUI user groups using the OWUI admin API. Identity is matched by email. Users not yet present in OWUI are skipped with INFO log. Deletes only remove users from the corresponding OWUI group.

## Quick Start

### 1. Start All Services

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps
```

### 2. Automatic OpenWebUI Setup

The system automatically:
- Generates API key for OpenWebUI
- Updates configuration with real API key
- Starts sync service with correct settings

### 3. Verify Operation

```bash
# Check sync service metrics
curl http://localhost:8000/metrics

# Check health endpoints
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

## Manual OpenWebUI Setup (if needed)

If automatic setup doesn't work, follow these steps:

### 1. Open OpenWebUI in browser
```
http://localhost:8080
```

### 2. Create admin account
- **Email**: `admin@example.com`
- **Password**: `adminpassword`

### 3. Create API key
1. Go to **Settings > Account**
2. Create new API key
3. Copy the key

### 4. Update configuration
```bash
# Save API key to file
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

### Group Mappings (config/config.yaml)

```yaml
group_mappings:
  - ldap_group_dn: "cn=dep1,ou=groups,dc=example,dc=com"
    target_group_name: "Demo Group A"
  - ldap_group_dn: "cn=dep2,ou=groups,dc=example,dc=com"
    target_group_name: "Demo Group B"
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
2. **OpenWebUI** - target system for synchronization
3. **Sync Service** - main synchronization service
4. **Mock API** - test API for development

### Components

- **LDAP Provider** - LDAP connection
- **OpenWebUI Adapter** - OpenWebUI API interaction
- **Sync Engine** - synchronization logic
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
2. Add configuration in `config/config.yaml`
3. Update `sync_service/services/sync_engine.py`
4. Add tests

## Troubleshooting

### OpenWebUI Issues

1. **OpenWebUI not responding**
   ```bash
   # Check status
   docker compose ps openwebui
   
   # Check logs
   docker compose logs openwebui
   ```

2. **API key not working**
   ```bash
   # Regenerate key
   python3 scripts/generate_api_key.py
   
   # Update configuration
   python3 scripts/update_config.py
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

The project includes comprehensive integration testing with real OpenWebUI:

1. **Real OpenWebUI API** - Tests against actual OpenWebUI endpoints
2. **LDAP Integration** - Real LDAP server with demo data
3. **End-to-End Sync** - Complete synchronization workflow
4. **Metrics Validation** - Prometheus metrics verification

### Test Results

**Successfully tested:**
- LDAP user and group discovery
- OpenWebUI API authentication
- Group membership synchronization
- User addition to groups
- User removal from groups (via group update)
- Metrics collection and monitoring
- Full bidirectional synchronization

## License

MIT License
