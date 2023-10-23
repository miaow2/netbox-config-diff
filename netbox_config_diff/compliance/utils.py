import re
from difflib import unified_diff

from django.forms import ChoiceField
from extras.scripts import ScriptVariable

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


class CustomChoiceVar(ScriptVariable):
    form_field = ChoiceField

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_attrs["choices"] = choices


def get_unified_diff(rendered_config: str, actual_config: str, device: str) -> str:
    diff = unified_diff(
        rendered_config.strip().splitlines(),
        actual_config.splitlines(),
        fromfiledate=device,
        tofiledate=device,
        lineterm="",
    )
    return "\n".join(diff).strip()


def exclude_lines(text: str, regexs: list) -> str:
    for item in regexs:
        text = re.sub(item, "", text, flags=re.I | re.M)
    return text.strip()
