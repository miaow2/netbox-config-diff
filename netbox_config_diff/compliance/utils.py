import re
from difflib import unified_diff

from django.forms import ChoiceField
from extras.scripts import ScriptVariable
from hier_config import Host

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

REMEDIATION_MAPPING = {
    "arista_eos": "eos",
    "cisco_iosxe": "ios",
    "cisco_iosxr": "iosxr",
    "cisco_nxos": "nxos",
    "juniper_junos": "junos",
    "vyos_vyos": "vyos",
}


class CustomChoiceVar(ScriptVariable):
    form_field = ChoiceField

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_attrs["choices"] = choices


def get_unified_diff(rendered_config: str, actual_config: str, device: str) -> str:
    diff = unified_diff(
        re.sub("\n{3,}", "\n", actual_config).splitlines(),
        re.sub("\n{3,}", "\n", rendered_config).strip().splitlines(),
        fromfiledate=device,
        tofiledate=device,
        lineterm="",
    )
    return "\n".join(diff).strip()


def exclude_lines(text: str, regexs: list) -> str:
    for item in regexs:
        text = re.sub(item, "", text, flags=re.I | re.M)
    return text.strip()


def get_remediation_commands(name: str, platform: str, actual_config: str, rendered_config: str) -> str:
    host = Host(hostname=name, os=REMEDIATION_MAPPING.get(platform, "ios"))
    host.load_running_config(config_text=actual_config)
    host.load_generated_config(config_text=rendered_config)
    return host.remediation_config_filtered_text(include_tags={}, exclude_tags={})


def get_diff_statistics(diff: str) -> tuple[int, int]:
    lines_added = 0
    lines_deleted = 0

    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            lines_added += 1
        elif line.startswith("-") and not line.startswith("---"):
            lines_deleted += 1

    return lines_added, lines_deleted
