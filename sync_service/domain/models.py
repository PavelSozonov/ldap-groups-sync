"""Domain models for sync service."""

from dataclasses import dataclass
from typing import Set


@dataclass
class UserIdentity:
    """Represents a user identity within a directory or service."""

    email: str


@dataclass
class GroupMapping:
    """Mapping between an LDAP group DN and target service group name."""

    ldap_group_dn: str
    target_group_name: str


@dataclass
class DiffResult:
    """Result of diffing two sets of user emails."""

    adds: Set[str]
    deletes: Set[str]
