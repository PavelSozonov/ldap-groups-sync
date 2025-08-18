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
        try:
            groups = self.adapter.list_groups()
            logger.info(f"Discovered {len(groups)} groups: {[g['name'] for g in groups]}")
            self.group_name_to_id = {g["name"]: g["id"] for g in groups}
            logger.info(f"Group name to ID mapping created: {self.group_name_to_id}")
        except Exception as e:
            logger.error(f"Failed to discover groups during initialization: {e}")
            logger.error(f"This will cause all sync iterations to fail until groups are discovered")
            self.group_name_to_id = {}

    def run_iteration(self) -> None:
        @self._retry
        def _run() -> None:
            start = perf_counter()
            logger.info(f"Starting sync iteration with {len(self.mappings)} mappings")
            
            try:
                all_users = {u["email"]: u["id"] for u in self.adapter.list_users()}
                logger.info(f"Found {len(all_users)} users: {list(all_users.keys())}")
            except Exception as e:
                logger.error(f"Failed to list users: {e}")
                raise
            
            try:
                all_groups = self.adapter.list_groups()
                logger.info(f"Found {len(all_groups)} groups: {[g['name'] for g in all_groups]}")
            except Exception as e:
                logger.error(f"Failed to list groups: {e}")
                raise
            
            logger.info(f"Group name to ID mapping: {self.group_name_to_id}")
            logger.info(f"Available group names: {list(self.group_name_to_id.keys())}")
            logger.info(f"Target group names from mappings: {[m.target_group_name for m in self.mappings]}")
            
            for mapping in self.mappings:
                logger.info(f"Processing mapping: {mapping.ldap_group_dn} -> {mapping.target_group_name}")
                group_id = self.group_name_to_id.get(mapping.target_group_name)
                logger.info(f"Found group_id: {group_id} for group: {mapping.target_group_name}")
                if not group_id:
                    logger.error(f"Group '{mapping.target_group_name}' not found in OpenWebUI. Available groups: {list(self.group_name_to_id.keys())}")
                    sync_errors_total.labels(target="owui", kind="missing_group").inc()
                    continue
                
                # Find the group and get its user_ids
                group = next((g for g in all_groups if g["id"] == group_id), None)
                if not group:
                    logger.error(f"Group object not found for group_id: {group_id}, target_group: {mapping.target_group_name}")
                    sync_errors_total.labels(target="owui", kind="missing_group").inc()
                    continue
                
                # Get user IDs in the group and map them to emails
                group_user_ids = group.get("user_ids", [])
                logger.info(f"Group '{mapping.target_group_name}' currently has user_ids: {group_user_ids}")
                
                target_emails = {u["email"] for u in self.adapter.list_users() if u["id"] in group_user_ids}
                email_to_id = {u["email"]: u["id"] for u in self.adapter.list_users() if u["id"] in group_user_ids}
                logger.info(f"Current users in group '{mapping.target_group_name}': {target_emails}")
                
                try:
                    ldap_emails = self.directory.get_group_members(mapping.ldap_group_dn)
                    logger.info(f"LDAP group '{mapping.ldap_group_dn}' has members: {ldap_emails}")
                except Exception as e:
                    logger.error(f"Failed to get LDAP group members for '{mapping.ldap_group_dn}': {e}")
                    continue
                
                adds, deletes = diff_members(ldap_emails, target_emails)
                logger.info(f"Sync plan for '{mapping.target_group_name}': add {adds}, remove {deletes}")
                
                for email in adds:
                    user_id = all_users.get(email)
                    if user_id:
                        logger.info(f"Adding user {email} (id: {user_id}) to group {mapping.target_group_name} (id: {group_id})")
                        try:
                            self.adapter.add_user_to_group(group_id, user_id)
                            owui_add_total.inc()
                            logger.info(f"Successfully added user {email} to group {mapping.target_group_name}")
                        except Exception as e:
                            logger.error(f"Failed to add user {email} to group {mapping.target_group_name}: {e}")
                    else:
                        logger.info(f"User {email} not found in OpenWebUI, skipping")
                        
                for email in deletes:
                    user_id = email_to_id.get(email)
                    if user_id:
                        logger.info(f"Removing user {email} (id: {user_id}) from group {mapping.target_group_name} (id: {group_id})")
                        try:
                            self.adapter.remove_user_from_group(group_id, user_id)
                            owui_delete_total.inc()
                            logger.info(f"Successfully removed user {email} from group {mapping.target_group_name}")
                        except Exception as e:
                            logger.error(f"Failed to remove user {email} from group {mapping.target_group_name}: {e}")
            duration = perf_counter() - start
            sync_iteration_seconds.observe(duration)
            logger.info(f"Sync iteration completed in {duration:.2f} seconds")

        _run()
