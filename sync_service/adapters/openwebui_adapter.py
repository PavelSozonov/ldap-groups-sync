"""OpenWebUI service adapter."""

from __future__ import annotations

from typing import Dict, Any

import httpx


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

    def list_groups(self) -> httpx.Response:
        return self.client.get(self._url("list_groups"))

    def list_users(self) -> httpx.Response:
        return self.client.get(self._url("list_users"))

    def list_group_users(self, group_id: str) -> httpx.Response:
        return self.client.get(self._url("group_users", group_id=group_id))

    def add_user_to_group(self, group_id: str, user_id: str) -> httpx.Response:
        url = self._url("add_user_to_group", group_id=group_id)
        return self.client.post(url, json={"user_id": user_id})

    def remove_user_from_group(self, group_id: str, user_id: str) -> httpx.Response:
        url = self._url("remove_user_from_group", group_id=group_id, user_id=user_id)
        return self.client.delete(url)
