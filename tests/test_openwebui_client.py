from sync_service.adapters.openwebui_adapter import OpenWebUIAdapter


def test_path_templating():
    adapter = OpenWebUIAdapter(base_url="http://localhost", api_key="x")
    url = adapter._url("group_users", group_id="123")
    assert url == "http://localhost/api/v1/groups/123/users"
