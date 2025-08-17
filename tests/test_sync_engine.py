from typing import Iterable, List

from sync_service.adapters.base import DirectoryProvider
from sync_service.adapters.openwebui_adapter import OpenWebUIAdapter
from sync_service.domain.models import GroupMapping
from sync_service.services.sync_engine import SyncEngine


class FakeDirectory(DirectoryProvider):
    def get_group_members(self, group_dn: str) -> Iterable[str]:
        return {"a@example.com", "b@example.com"}


class FakeAdapter(OpenWebUIAdapter):
    def __init__(self) -> None:  # type: ignore[override]
        self.groups = [{"id": "1", "name": "grp"}]
        self.users = [
            {"id": "10", "email": "b@example.com"},
            {"id": "11", "email": "c@example.com"},
            {"id": "12", "email": "a@example.com"},
        ]
        self.group_members = {
            "1": [
                {"id": "10", "email": "b@example.com"},
                {"id": "11", "email": "c@example.com"},
            ]
        }
        self.added: List[tuple[str, str]] = []
        self.removed: List[tuple[str, str]] = []

    def list_groups(self):  # type: ignore[override]
        return self.groups

    def list_users(self):  # type: ignore[override]
        return self.users

    def list_group_users(self, group_id: str):  # type: ignore[override]
        return self.group_members[group_id]

    def add_user_to_group(self, group_id: str, user_id: str) -> None:  # type: ignore[override]
        self.added.append((group_id, user_id))

    def remove_user_from_group(self, group_id: str, user_id: str) -> None:  # type: ignore[override]
        self.removed.append((group_id, user_id))


def test_sync_engine_adds_and_deletes():
    directory = FakeDirectory()
    adapter = FakeAdapter()
    mapping = GroupMapping(
        ldap_group_dn="cn=grp,dc=example,dc=com",
        target_group_name="grp",
    )
    engine = SyncEngine(directory, adapter, [mapping])
    engine.run_iteration()
    assert adapter.added == [("1", "12")]
    assert adapter.removed == [("1", "11")]
