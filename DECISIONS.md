# Decisions

- Identity matched by email.
- Sequential sync per mapping.
- Retry policy uses exponential backoff with jitter.
- TLS verification disabled by default for demo; enable in production.
