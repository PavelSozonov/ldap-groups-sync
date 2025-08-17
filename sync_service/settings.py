"""Application settings using Pydantic."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel


class ServiceConfig(BaseModel):
    type: str
    name: str
    base_url: str
    auth: dict
    http: dict | None = None
    path_templates: dict | None = None
    group_mappings: list[dict]


class AppConfig(BaseModel):
    version: int
    identity: dict
    ldap: dict
    services: list[ServiceConfig]
    sync: dict


def load_config(path: Path) -> AppConfig:
    """Load YAML config file with env interpolation and parse into AppConfig."""
    raw = os.path.expandvars(path.read_text())
    data = yaml.safe_load(raw)
    return AppConfig.model_validate(data)
