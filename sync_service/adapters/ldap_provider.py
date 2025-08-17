"""LDAP directory provider using ldap3."""

from __future__ import annotations

import ssl
from typing import Iterable, List

from ldap3 import Connection, Server, Tls

from .base import DirectoryProvider
from ..metrics import ldap_lookup_errors_total, track_external_request


class LDAPProvider(DirectoryProvider):
    """Directory provider for Active Directory via LDAP."""

    def __init__(
        self,
        url: str,
        bind_dn: str,
        bind_password: str,
        base_dn: str,
        group_object_class: str,
        membership_attr: str,
        user_filter: str,
        identity_attr: str,
        verify_tls: bool = False,
        timeout: int = 10,
        connection: Connection | None = None,
    ) -> None:
        self.base_dn = base_dn
        self.group_object_class = group_object_class
        self.membership_attr = membership_attr
        self.user_filter = user_filter
        self.identity_attr = identity_attr
        if connection is not None:
            self.conn = connection
        else:
            tls_config = Tls(
                validate=ssl.CERT_REQUIRED if verify_tls else ssl.CERT_NONE
            )
            server = Server(url, use_ssl=url.startswith("ldaps"), tls=tls_config)
            self.conn = Connection(
                server,
                user=bind_dn,
                password=bind_password,
                receive_timeout=timeout,
                auto_bind=True,
            )

    def get_group_members(self, group_dn: str) -> Iterable[str]:
        """Return iterable of member emails for given group DN."""
        emails: List[str] = []
        with track_external_request("ldap"):
            self.conn.search(
                search_base=group_dn,
                search_filter=f"(objectClass={self.group_object_class})",
                attributes=[self.membership_attr],
            )
        if not self.conn.entries:
            return emails
        members = self.conn.entries[0][self.membership_attr].values
        for dn in members:
            with track_external_request("ldap"):
                self.conn.search(
                    search_base=dn,
                    search_filter=self.user_filter,
                    attributes=[self.identity_attr],
                )
            if not self.conn.entries:
                ldap_lookup_errors_total.inc()
                continue
            mail = self.conn.entries[0][self.identity_attr].value
            if mail:
                emails.append(str(mail))
        return emails
