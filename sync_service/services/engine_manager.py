"""Engine manager for handling multiple sync engines."""

from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from typing import Dict, List

from .sync_engine import SyncEngine
from ..adapters.ldap_provider import LDAPProvider
from ..adapters.factory import create_service_adapter
from ..domain.models import GroupMapping
from ..settings import AppConfig
from ..metrics import sync_iterations_total, last_sync_timestamp_seconds

logger = logging.getLogger(__name__)


class EngineManager:
    """Manages multiple sync engines running in parallel."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.engines: Dict[str, SyncEngine] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.running = False

    def _build_engine_for_service(self, service_config) -> SyncEngine:
        """Build a sync engine for a specific service."""
        # Create LDAP provider (shared across all engines)
        ldap_cfg = self.config.ldap
        identity_attr = self.config.identity["user_attribute"]
        ldap_provider = LDAPProvider(
            url=ldap_cfg["url"],
            bind_dn=ldap_cfg["bind_dn"],
            bind_password=ldap_cfg["bind_password"],
            base_dn=ldap_cfg["base_dn"],
            group_object_class=ldap_cfg["group"]["object_class"],
            membership_attr=ldap_cfg["group"]["membership_attr"],
            user_filter=ldap_cfg["user_filter"],
            identity_attr=identity_attr,
            verify_tls=ldap_cfg.get("tls", {}).get("verify", False),
        )

        # Create service adapter
        adapter = create_service_adapter(service_config.model_dump())
        
        # Create group mappings
        mappings = [GroupMapping(**m) for m in service_config.group_mappings]
        
        # Get sync configuration (service-specific or global fallback)
        sync_cfg = getattr(service_config, 'sync', None) or self.config.sync
        
        return SyncEngine(
            directory=ldap_provider,
            adapter=adapter,
            mappings=mappings,
            retries=sync_cfg.get("retries", 3),
            backoff_base_seconds=sync_cfg.get("backoff_base_seconds", 0.5),
            max_backoff_seconds=sync_cfg.get("max_backoff_seconds", 10.0),
        )

    def build_engines(self) -> None:
        """Build engines for all configured services."""
        for service_config in self.config.services:
            service_name = service_config.name
            logger.info(f"Building engine for service: {service_name}")
            
            try:
                engine = self._build_engine_for_service(service_config)
                self.engines[service_name] = engine
                logger.info(f"Successfully built engine for service: {service_name}")
            except Exception as e:
                logger.error(f"Failed to build engine for service {service_name}: {e}")

    async def _run_engine_loop(self, service_name: str, engine: SyncEngine) -> None:
        """Run sync loop for a specific engine."""
        service_config = next(s for s in self.config.services if s.name == service_name)
        sync_cfg = getattr(service_config, 'sync', None) or self.config.sync
        interval = sync_cfg.get("interval_seconds", 60)
        
        logger.info(f"Starting sync loop for service: {service_name} (interval: {interval}s)")
        
        while self.running:
            try:
                sync_iterations_total.inc()
                engine.run_iteration()
                last_sync_timestamp_seconds.set_to_current_time()
                logger.debug(f"Completed sync iteration for service: {service_name}")
            except Exception as exc:
                logger.error(f"Sync iteration failed for service {service_name}: {exc}")
            
            await asyncio.sleep(interval)

    async def start(self) -> None:
        """Start all engines."""
        if self.running:
            logger.warning("Engine manager is already running")
            return

        self.running = True
        logger.info(f"Starting {len(self.engines)} sync engines")

        for service_name, engine in self.engines.items():
            task = asyncio.create_task(
                self._run_engine_loop(service_name, engine),
                name=f"sync-{service_name}"
            )
            self.tasks[service_name] = task
            logger.info(f"Started sync task for service: {service_name}")

    async def stop(self) -> None:
        """Stop all engines."""
        if not self.running:
            return

        logger.info("Stopping all sync engines")
        self.running = False

        # Cancel all tasks
        for service_name, task in self.tasks.items():
            task.cancel()
            logger.info(f"Cancelled sync task for service: {service_name}")

        # Wait for all tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
            self.tasks.clear()

        logger.info("All sync engines stopped")

    def get_engine_status(self) -> Dict[str, str]:
        """Get status of all engines."""
        status = {}
        for service_name, task in self.tasks.items():
            if task.done():
                status[service_name] = "stopped"
            elif task.cancelled():
                status[service_name] = "cancelled"
            else:
                status[service_name] = "running"
        return status
