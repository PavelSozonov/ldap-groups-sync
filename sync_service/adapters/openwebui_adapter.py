"""OpenWebUI service adapter."""

from __future__ import annotations

from typing import Any, Dict, List

import httpx

from ..metrics import owui_http_errors_total, track_external_request


class OpenWebUIAdapter:
    """Adapter to interact with Open WebUI API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        path_templates: Dict[str, str] | None = None,
        timeout: float = 10.0,
        verify_tls: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.path_templates = {
            "list_groups": "/api/v1/groups",
            "group_users": "/api/v1/groups/{group_id}/users",
            "add_user_to_group": "/api/v1/groups/{group_id}/users/add",
            "remove_user_from_group": "/api/v1/groups/{group_id}/users/{user_id}/remove",
            "list_users": "/api/v1/users",
        }
        if path_templates:
            self.path_templates.update(path_templates)
        self.client = httpx.Client(
            timeout=timeout,
            verify=verify_tls,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def _url(self, key: str, **params: Any) -> str:
        template = self.path_templates[key]
        return self.base_url + template.format(**params)

    def list_groups(self) -> List[Dict[str, Any]]:
        with track_external_request("owui"):
            resp = self.client.get(self._url("list_groups"))
        if resp.is_error:
            owui_http_errors_total.inc()
            resp.raise_for_status()
        print(f"Response status: {resp.status_code}")
        print(f"Response text: {resp.text}")
        return resp.json()

    def list_users(self) -> List[Dict[str, Any]]:
        with track_external_request("owui"):
            resp = self.client.get(self._url("list_users"))
        if resp.is_error:
            owui_http_errors_total.inc()
            resp.raise_for_status()
        data = resp.json()
        # OpenWebUI returns {"users": [...], "total": N} format
        if isinstance(data, dict) and "users" in data:
            return data["users"]
        return data

    def list_group_users(self, group_id: str) -> List[Dict[str, Any]]:
        with track_external_request("owui"):
            resp = self.client.get(self._url("group_users", group_id=group_id))
        if resp.is_error:
            owui_http_errors_total.inc()
            resp.raise_for_status()
        return resp.json()

    def add_user_to_group(self, group_id: str, user_id: str) -> None:
        url = self._url("add_user_to_group", group_id=group_id)
        with track_external_request("owui"):
            resp = self.client.post(url, json={"user_ids": [user_id]})
        if resp.is_error:
            owui_http_errors_total.inc()
            resp.raise_for_status()

    def remove_user_from_group(self, group_id: str, user_id: str) -> None:
        url = self._url("remove_user_from_group", group_id=group_id, user_id=user_id)
        with track_external_request("owui"):
            resp = self.client.delete(url)
        if resp.is_error:
            owui_http_errors_total.inc()
            resp.raise_for_status()

    def update_group_users(self, group_id: str, user_ids: List[str], group_name: str, group_description: str = "") -> None:
        """Update the entire user list for a group."""
        url = self._url("update_group", group_id=group_id)
        data = {
            "name": group_name,
            "description": group_description,
            "user_ids": user_ids
        }
        with track_external_request("owui"):
            resp = self.client.post(url, json=data)
        if resp.is_error:
            owui_http_errors_total.inc()
            resp.raise_for_status()
