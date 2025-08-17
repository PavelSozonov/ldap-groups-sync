"""Base adapter interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class DirectoryProvider(ABC):
    """Abstract interface for LDAP-like providers."""

    @abstractmethod
    def get_group_members(self, group_dn: str) -> Iterable[str]:
        """Return iterable of member emails for given group DN."""


class ServiceAdapter(ABC):
    """Abstract interface for target services."""

    @abstractmethod
    def list_group_members(self, group_id: str) -> Iterable[str]:
        """Return member emails for group."""

    @abstractmethod
    def add_user_to_group(self, group_id: str, email: str) -> None:
        """Add user to group by email."""

    @abstractmethod
    def remove_user_from_group(self, group_id: str, email: str) -> None:
        """Remove user from group by email."""
