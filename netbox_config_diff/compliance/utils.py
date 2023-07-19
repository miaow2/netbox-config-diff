import re
from difflib import unified_diff


def get_unified_diff(rendered_config: str, actual_config: str, device: str) -> str:
    diff = unified_diff(
        rendered_config.splitlines(), actual_config.splitlines(), fromfiledate=device, tofiledate=device, lineterm=""
    )
    return "\n".join(diff).strip()


def exclude_lines(text: str, regex: str) -> str:
    for item in regex.splitlines():
        text = re.sub(item, "", text, flags=re.MULTILINE)
    return text
