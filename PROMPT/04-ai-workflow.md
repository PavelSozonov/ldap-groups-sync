# AI Workflow

## Core Principles

### Prompt-as-Code
- Keep specification files under version control
- All requirements and decisions documented in PROMPT/ directory
- Changes to requirements must update PROMPT files and DECISIONS.md

### Iterative Development
- Scaffold -> adapters -> sync engine -> engine manager -> tests
- Each iteration builds upon the previous one
- Validate each step before proceeding

### Quality Assurance
- After each change: run formatting, linting, type checking, tests
- Maintain code quality throughout development
- Document decisions and rationale

## Development Process

### 1. Planning Phase
- Review project requirements in PROMPT/02-project-spec.md
- Check common rules in PROMPT/01-common-rules.md
- Update DECISIONS.md with architectural decisions

### 2. Implementation Phase
- Follow iterative approach: scaffold -> adapters -> sync engine -> engine manager -> tests
- Implement features incrementally
- Run quality checks after each change

### 3. Testing Phase
- Unit tests for individual components
- Integration tests with real services
- End-to-end testing with complete workflow

### 4. Documentation Phase
- Update README.md with usage instructions
- Document API changes and configurations
- Update DECISIONS.md with implementation details

## Quality Gates

### Code Quality
- [ ] Code formatting (black, ruff)
- [ ] Linting (ruff)
- [ ] Type checking (mypy)
- [ ] Unit tests passing
- [ ] Integration tests passing

### Documentation
- [ ] README.md updated
- [ ] DECISIONS.md updated
- [ ] PROMPT files updated if needed
- [ ] Code comments in English

### Testing
- [ ] Unit test coverage
- [ ] Integration test coverage
- [ ] End-to-end test validation
- [ ] Performance testing if applicable

## Integration Testing Workflow

### 1. Setup Environment
- Start all services with `docker compose up -d`
- Verify services are healthy
- Check API connectivity

### 2. Manual Testing
- Create test data in LDAP
- Create test groups in target services
- Verify synchronization works for all engines

### 3. Automated Testing
- Run integration tests
- Verify metrics collection
- Check error handling
- Validate multi-engine operation

### 4. Validation
- Confirm sync service operates correctly
- Verify monitoring and observability
- Validate engine status endpoint
- Document any issues found

## Maintenance

### Regular Updates
- Keep dependencies updated
- Monitor for security vulnerabilities
- Update documentation as needed

### Monitoring
- Track metrics and performance
- Monitor error rates
- Update configurations as needed
