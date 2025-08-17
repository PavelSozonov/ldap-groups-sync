from pathlib import Path

from sync_service.settings import load_config


def test_load_config_env_interpolation(monkeypatch):
    monkeypatch.setenv("LDAP_URL", "ldap://example")
    cfg = load_config(Path("config/config.yaml"))
    assert cfg.ldap["url"] == "ldap://example"
