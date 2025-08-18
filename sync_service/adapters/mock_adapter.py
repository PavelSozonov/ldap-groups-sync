"""Mock adapter for testing purposes."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Iterable

from .base import ServiceAdapter

logger = logging.getLogger(__name__)


class MockAdapter(ServiceAdapter):
    """Mock adapter for testing purposes."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        path_templates: Dict[str, str] | None = None,
        timeout: int = 10,
        verify_tls: bool = False,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.path_templates = path_templates or {}
        self.timeout = timeout
        self.verify_tls = verify_tls
        
        # Mock data
        self.mock_groups = [
            {"id": "mock-group-1", "name": "Mock Group 1", "user_ids": []},
            {"id": "mock-group-2", "name": "Mock Group 2", "user_ids": []},
        ]
        self.mock_users = [
            {"id": "mock-user-1", "email": "demo@example.com"},
        ]

    def _url(self, key: str, **params: Any) -> str:
        """Build URL from template."""
        template = self.path_templates.get(key, "")
        return self.base_url + template.format(**params)

    def list_groups(self) -> List[Dict[str, Any]]:
        """List all groups."""
        logger.info("Mock: listing groups")
        return self.mock_groups

    def list_users(self) -> List[Dict[str, Any]]:
        """List all users."""
        logger.info("Mock: listing users")
        return self.mock_users

    def list_group_users(self, group_id: str) -> List[Dict[str, Any]]:
        """List users in a group."""
        logger.info(f"Mock: listing users for group {group_id}")
        group = next((g for g in self.mock_groups if g["id"] == group_id), None)
        if group:
            return [u for u in self.mock_users if u["id"] in group["user_ids"]]
        return []

    def list_group_members(self, group_id: str) -> Iterable[str]:
        """Return member emails for group."""
        logger.info(f"Mock: listing group members for group {group_id}")
        group = next((g for g in self.mock_groups if g["id"] == group_id), None)
        if group:
            return [u["email"] for u in self.mock_users if u["id"] in group["user_ids"]]
        return []

    def add_user_to_group(self, group_id: str, user_id: str) -> None:
        """Add user to group."""
        logger.info(f"Mock: adding user {user_id} to group {group_id}")
        group = next((g for g in self.mock_groups if g["id"] == group_id), None)
        if group and user_id not in group["user_ids"]:
            group["user_ids"].append(user_id)

    def remove_user_from_group(self, group_id: str, user_id: str) -> None:
        """Remove user from group."""
        logger.info(f"Mock: removing user {user_id} from group {group_id}")
        group = next((g for g in self.mock_groups if g["id"] == group_id), None)
        if group and user_id in group["user_ids"]:
            group["user_ids"].remove(user_id)

    def update_group_users(self, group_id: str, user_ids: List[str], group_name: str, group_description: str = "") -> None:
        """Update group with new user list."""
        logger.info(f"Mock: updating group {group_id} with users {user_ids}")
        group = next((g for g in self.mock_groups if g["id"] == group_id), None)
        if group:
            group["user_ids"] = user_ids
            group["name"] = group_name
