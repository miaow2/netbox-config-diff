import re
from difflib import unified_diff

PLATFORM_MAPPING = {
    "arista_eos": "arista_eos",
    "cisco_aireos": "cisco_aireos",
    "aruba_aoscx": "aruba_aoscx",
    "cisco_asa": "cisco_asa",
    "cisco_iosxe": "cisco_ios",
    "cisco_iosxr": "cisco_iosxr",
    "cisco_nxos": "cisco_nxos",
    "juniper_junos": "juniper_junos",
    "mikrotik_routeros": "mikrotik_routeros",
    "nokia_sros": "nokia_sros",
    "paloalto_panos": "paloalto_panos",
    "ruckus_fastiron": "ruckus_fastiron",
}


def get_unified_diff(rendered_config: str, actual_config: str, device: str) -> str:
    diff = unified_diff(
        rendered_config.splitlines(),
        actual_config.splitlines(),
        fromfiledate=device,
        tofiledate=device,
        lineterm="",
    )
    return "\n".join(diff).strip()


def exclude_lines(text: str, regex: str) -> str:
    for item in regex.splitlines():
        text = re.sub(item, "", text, flags=re.MULTILINE)
    return text
