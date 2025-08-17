"""Factory for service adapters based on config."""

from __future__ import annotations

from typing import Any, Dict

from .openwebui_adapter import OpenWebUIAdapter


def create_service_adapter(cfg: Dict[str, Any]) -> Any:
    """Create adapter from config dictionary."""
    adapter_type = cfg.get("type")
    if adapter_type == "openwebui":
        return OpenWebUIAdapter(
            base_url=cfg["base_url"],
            api_key=cfg["auth"]["api_key"],
            path_templates=cfg.get("path_templates"),
            timeout=cfg.get("http", {}).get("request_timeout_seconds", 10),
            verify_tls=cfg.get("http", {}).get("verify_tls", False),
        )
    raise ValueError(f"Unsupported adapter type: {adapter_type}")
