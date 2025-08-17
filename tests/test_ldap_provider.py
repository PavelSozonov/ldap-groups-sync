from ldap3 import Connection, Server, MOCK_SYNC

from sync_service.adapters.ldap_provider import LDAPProvider


def build_mock_connection() -> Connection:
    server = Server("mocked", get_info=MOCK_SYNC)
    conn = Connection(
        server,
        user="cn=admin,dc=example,dc=com",
        password="pw",
        client_strategy=MOCK_SYNC,
    )
    conn.bind()
    conn.strategy.add_entry(
        "cn=group,dc=example,dc=com",
        {"objectClass": ["group"], "member": ["cn=user1,dc=example,dc=com"]},
    )
    conn.strategy.add_entry(
        "cn=user1,dc=example,dc=com",
        {"objectClass": ["user"], "mail": "user1@example.com"},
    )
    return conn


def test_get_group_members():
    conn = build_mock_connection()
    provider = LDAPProvider(
        url="ldap://mocked",
        bind_dn="cn=admin,dc=example,dc=com",
        bind_password="pw",
        base_dn="dc=example,dc=com",
        group_object_class="group",
        membership_attr="member",
        user_filter="(objectClass=user)",
        identity_attr="mail",
        connection=conn,
    )
    members = list(provider.get_group_members("cn=group,dc=example,dc=com"))
    assert members == ["user1@example.com"]
