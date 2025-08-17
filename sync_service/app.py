"""FastAPI application."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
import logging
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Response

from .settings import load_config
from .metrics import export_metrics, last_sync_timestamp_seconds, sync_iterations_total
from .logging_conf import configure_logging
from .adapters.ldap_provider import LDAPProvider
from .adapters.factory import create_service_adapter
from .domain.models import GroupMapping
from .services.sync_engine import SyncEngine

config_path = Path("config/config.yaml")
app_config = load_config(config_path)
ready = False


def _build_engine() -> SyncEngine:
    ldap_cfg = app_config.ldap
    identity_attr = app_config.identity["user_attribute"]
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
    service_cfg = next(s for s in app_config.services if s.type == "openwebui")
    adapter = create_service_adapter(service_cfg.model_dump())
    mappings = [GroupMapping(**m) for m in service_cfg.group_mappings]
    sync_cfg = app_config.sync
    return SyncEngine(
        directory=ldap_provider,
        adapter=adapter,
        mappings=mappings,
        retries=sync_cfg.get("retries", 3),
        backoff_base_seconds=sync_cfg.get("backoff_base_seconds", 0.5),
        max_backoff_seconds=sync_cfg.get("max_backoff_seconds", 10.0),
    )


engine = _build_engine()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global ready
    configure_logging()

    async def sync_loop() -> None:
        global ready
        ready = True
        while True:
            sync_iterations_total.inc()
            try:
                engine.run_iteration()
                last_sync_timestamp_seconds.set_to_current_time()
            except Exception as exc:  # noqa: BLE001
                logger.error("sync_iteration_failed", extra={"error": str(exc)})
            await asyncio.sleep(app_config.sync.get("interval_seconds", 60))

    task = asyncio.create_task(sync_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    return {"ready": str(ready).lower()}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(export_metrics(), media_type="text/plain; version=0.0.4")


@app.get("/version")
async def version() -> dict[str, str]:
    return {"version": "0.1.0"}
