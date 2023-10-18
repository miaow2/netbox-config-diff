import pytest

from netbox_config_diff.compliance.utils import exclude_lines, get_unified_diff

RENDERED_CONFIG = """hostname test-1

interface fa-0/0
  switchport mode access
  switchport access vlan 10
"""

ACTUAL_CONFIG = """hostname test-1

interface fa-0/0
  switchport mode access
  switchport access vlan 100
"""


@pytest.mark.parametrize(
    "regex, expected",
    [
        (
            "^interface.?\n^Building",
            "hostname test-1\n\nfa-0/0\n  switchport mode access\n  switchport access vlan 100",
        ),
        (
            "^interface.*$\n^Building",
            "hostname test-1\n\n\n  switchport mode access\n  switchport access vlan 100",
        ),
        (
            "^Building",
            "hostname test-1\n\ninterface fa-0/0\n  switchport mode access\n  switchport access vlan 100",
        ),
    ],
    ids=["part of line", "full line", "no effect"],
)
def test_exclude_lines(regex: str, expected: str) -> None:
    assert exclude_lines(ACTUAL_CONFIG, regex.splitlines()) == expected


@pytest.mark.parametrize(
    "render, actual, expected",
    [
        (
            RENDERED_CONFIG,
            ACTUAL_CONFIG,
            "--- \ttest-1\n+++ \ttest-1\n@@ -2,4 +2,4 @@\n \n interface fa-0/0\n   switchport mode access\n-  switchport access vlan 10\n+  switchport access vlan 100",  # noqa
        ),
        (
            RENDERED_CONFIG,
            RENDERED_CONFIG,
            "",
        ),
    ],
    ids=["diff", "no diff"],
)
def test_get_unified_diff(render: str, actual: str, expected: str) -> None:
    assert get_unified_diff(render, actual, "test-1") == expected
