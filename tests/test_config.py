from pathlib import Path

from sync_service.settings import load_config


def test_load_config():
    cfg = load_config(Path("config/config.yaml"))
    assert cfg.ldap["url"] == "ldap://openldap:1389"
    assert cfg.ldap["bind_dn"] == "cn=admin,dc=example,dc=com"
