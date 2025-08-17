"""Set diff logic for group membership reconciliation."""

from typing import Iterable, Set


def diff_members(
    ldap_emails: Iterable[str], target_emails: Iterable[str]
) -> tuple[Set[str], Set[str]]:
    """Compute adds and deletes given two iterables of emails."""
    ldap_set = set(ldap_emails)
    target_set = set(target_emails)
    adds = ldap_set - target_set
    deletes = target_set - ldap_set
    return adds, deletes
