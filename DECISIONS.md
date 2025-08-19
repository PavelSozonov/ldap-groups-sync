# Architecture Decisions

## Core Design Decisions

### Identity Matching
- **Decision**: Identity matched by email address
- **Rationale**: Email is a common identifier across LDAP and OpenWebUI systems
- **Implementation**: Uses `mail` attribute from LDAP and `email` field from OpenWebUI

### Synchronization Strategy
- **Decision**: Sequential sync per mapping
- **Rationale**: Ensures consistency and prevents race conditions
- **Implementation**: Processes each group mapping one at a time

### Error Handling
- **Decision**: Retry policy uses exponential backoff with jitter
- **Rationale**: Prevents thundering herd and provides resilience
- **Implementation**: Configurable retries with bounded backoff

### Security
- **Decision**: TLS verification disabled by default for demo; enable in production
- **Rationale**: Simplifies development while maintaining security in production
- **Implementation**: Configurable via `verify_tls` setting

## API Design Decisions

### OpenWebUI API Integration
- **Decision**: Use OpenWebUI REST API with Bearer token authentication
- **Rationale**: Standard REST API approach with secure authentication
- **Implementation**: HTTP client with Authorization header

### Group Membership Management
- **Decision**: Use `user_ids` array format for adding users to groups
- **Rationale**: OpenWebUI API expects array format for multiple users
- **Implementation**: `{"user_ids": ["user_id1", "user_id2"]}`

### User Removal Strategy
- **Decision**: Use group update API instead of individual user removal
- **Rationale**: OpenWebUI DELETE endpoints return 405 Method Not Allowed
- **Implementation**: POST to `/api/v1/groups/id/{group_id}/update` with complete user list
- **Benefits**: Atomic operation, avoids API compatibility issues

### Health Checks
- **Decision**: Separate `/healthz` and `/readyz` endpoints
- **Rationale**: Kubernetes best practices for liveness and readiness probes
- **Implementation**: FastAPI endpoints with appropriate status codes

## Monitoring Decisions

### Metrics Collection
- **Decision**: Prometheus metrics for observability
- **Rationale**: Industry standard for metrics collection and monitoring
- **Implementation**: Prometheus client library with custom metrics

### Logging Strategy
- **Decision**: Structured JSON logging
- **Rationale**: Machine-readable logs for better analysis
- **Implementation**: Python logging with JSON formatter

## Container Decisions

### Docker Image
- **Decision**: Python 3.12 slim base image
- **Rationale**: Latest stable Python with minimal attack surface
- **Implementation**: Multi-stage build with non-root user

### Health Checks
- **Decision**: Health checks defined in K8s manifests, not Dockerfile
- **Rationale**: More flexible configuration for different environments
- **Implementation**: Removed HEALTHCHECK from Dockerfile

## Testing Decisions

### Multi-Engine Architecture
- **Decision**: Support multiple sync engines running in parallel
- **Rationale**: Enables synchronization to multiple target services simultaneously
- **Implementation**: EngineManager class with asyncio tasks for each service

### Integration Testing
- **Decision**: Real OpenWebUI API and Mock API for integration tests
- **Rationale**: Ensures compatibility with actual API behavior and provides validation
- **Implementation**: Docker Compose with real OpenWebUI container and mock service

### Mock API
- **Decision**: Maintain mock API for development and testing
- **Rationale**: Faster development cycles and validation of multi-engine functionality
- **Implementation**: FastAPI mock server with realistic responses and MockAdapter

## Implementation Decisions

### LDAP Configuration
- **Decision**: Use `groupOfNames` objectClass and `inetOrgPerson` for users
- **Rationale**: Compatible with Bitnami OpenLDAP container defaults
- **Implementation**: Updated `config.yaml` with correct objectClass values

### OpenWebUI API Endpoints
- **Decision**: Use specific endpoint patterns for different operations
- **Implementation**:
  - List groups: `/api/v1/groups/`
  - List users: `/api/v1/users/` (returns `{"users": [...], "total": N}`)
  - Add users: `/api/v1/groups/id/{group_id}/users/add`
  - Update group: `/api/v1/groups/id/{group_id}/update`

### Service Configuration
- **Decision**: Each service must have explicit sync configuration
- **Rationale**: Eliminates confusion and makes configuration explicit
- **Implementation**: Required sync field in ServiceConfig, no global fallback

### Engine Management
- **Decision**: Use asyncio tasks for parallel engine execution
- **Rationale**: Enables true parallelism and independent engine operation
- **Implementation**: EngineManager with task lifecycle management
