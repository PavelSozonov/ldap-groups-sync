"""Sync engine orchestrating LDAP and service reconciliation."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Dict, List

from ..adapters.base import DirectoryProvider
from ..adapters.openwebui_adapter import OpenWebUIAdapter
from ..domain.models import GroupMapping
from ..metrics import (
    owui_add_total,
    owui_delete_total,
    sync_errors_total,
    sync_iteration_seconds,
)
from ..retry import retry_on_exception
from .mappers import diff_members

logger = logging.getLogger(__name__)


class SyncEngine:
    """Coordinates group membership sync across mappings."""

    def __init__(
        self,
        directory: DirectoryProvider,
        adapter: OpenWebUIAdapter,
        mappings: List[GroupMapping],
        retries: int = 3,
        backoff_base_seconds: float = 0.5,
        max_backoff_seconds: float = 10.0,
    ) -> None:
        self.directory = directory
        self.adapter = adapter
        self.mappings = mappings
        self._retry = retry_on_exception(
            retries, backoff_base_seconds, max_backoff_seconds
        )
        self.group_name_to_id: Dict[str, str] = {}
        self._discover_groups()

    def _discover_groups(self) -> None:
        """Populate mapping of group name to id from target service."""
        groups = self.adapter.list_groups()
        self.group_name_to_id = {g["name"]: g["id"] for g in groups}

    def run_iteration(self) -> None:
        @self._retry
        def _run() -> None:
            start = perf_counter()
            all_users = {u["email"]: u["id"] for u in self.adapter.list_users()}
            all_groups = self.adapter.list_groups()
            for mapping in self.mappings:
                group_id = self.group_name_to_id.get(mapping.target_group_name)
                if not group_id:
                    logger.error(
                        "group_missing",
                        extra={"target_group": mapping.target_group_name},
                    )
                    sync_errors_total.labels(target="owui", kind="missing_group").inc()
                    continue
                
                # Find the group and get its user_ids
                group = next((g for g in all_groups if g["id"] == group_id), None)
                if not group:
                    logger.error(
                        "group_not_found",
                        extra={"group_id": group_id, "target_group": mapping.target_group_name},
                    )
                    sync_errors_total.labels(target="owui", kind="missing_group").inc()
                    continue
                
                # Get user IDs in the group and map them to emails
                group_user_ids = group.get("user_ids", [])
                group_users = [u for u in all_users.values() if u in group_user_ids]
                target_emails = {u["email"] for u in self.adapter.list_users() if u["id"] in group_user_ids}
                email_to_id = {u["email"]: u["id"] for u in self.adapter.list_users() if u["id"] in group_user_ids}
                
                ldap_emails = self.directory.get_group_members(mapping.ldap_group_dn)
                adds, deletes = diff_members(ldap_emails, target_emails)
                
                for email in adds:
                    user_id = all_users.get(email)
                    if user_id:
                        self.adapter.add_user_to_group(group_id, user_id)
                        owui_add_total.inc()
                    else:
                        logger.info("user_missing", extra={"email": email})
                for email in deletes:
                    user_id = email_to_id.get(email)
                    if user_id:
                        self.adapter.remove_user_from_group(group_id, user_id)
                        owui_delete_total.inc()
            duration = perf_counter() - start
            sync_iteration_seconds.observe(duration)

        _run()
