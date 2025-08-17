from sync_service.services.mappers import diff_members


def test_diff_members():
    adds, deletes = diff_members(
        ["a@example.com", "b@example.com"], ["b@example.com", "c@example.com"]
    )
    assert adds == {"a@example.com"}
    assert deletes == {"c@example.com"}
