from hier_config import Host

def _build_delete_ordering(max_depth: int = 10) -> list[dict]:
    """Build ordering rules that push delete commands after additions at any depth."""
    rules = []
    for depth in range(1, max_depth + 1):
        lineage = [{"anything": True}] * (depth - 1) + [{"startswith": "delete"}]
        rules.append({"lineage": lineage, "order": 700})
    return rules


SROS_OPTIONS: dict = {
    "style": "sros",
    "negation": "delete",
    "syntax_style": "cisco",
    "sectional_overwrite": [],
    "sectional_overwrite_no_negate": [],
    "ordering": _build_delete_ordering(),
    "indent_adjust": [],
    "parent_allows_duplicate_child": [],
    "sectional_exiting": [],
    "full_text_sub": [],
    "per_line_sub": [
        {"search": "^#.*", "replace": ""},
        {"search": "^\\s*##.*", "replace": ""},
    ],
    "idempotent_commands": [],
    "idempotent_commands_blacklist": [],
    "negation_default_when": [],
    "negation_negate_with": [],
}

INDENT = "    "


def _braces_to_indented(config: str) -> str:
    """Convert MD-CLI brace-delimited format to indentation-based format.

    Input:
        configure {
            router "Base" {
                bgp {
                    admin-state enable
                }
            }
        }

    Output:
        configure
            router "Base"
                bgp
                    admin-state enable
    """
    lines = []
    depth = 0

    for line in config.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "}":
            depth -= 1
            continue

        if stripped.endswith("{"):
            text = stripped[:-1].strip()
            if text:
                lines.append(INDENT * depth + text)
            depth += 1
            continue

        if stripped.endswith("{ }"):
            text = stripped[:-3].strip()
            if text:
                lines.append(INDENT * depth + text)
            continue

        lines.append(INDENT * depth + stripped)

    return "\n".join(lines)


def _indented_to_braces(text: str) -> str:
    """Convert indentation-based remediation output to MD-CLI brace format.

    Input (from hier_config remediation):
        configure
          router "Base"
            delete interface "old-if"
            bgp
              connect-retry 90
            interface "new-if"
              admin-state enable

    Output:
        configure {
            router "Base" {
                delete {
                    interface "old-if"
                }
                bgp {
                    connect-retry 90
                }
                interface "new-if" {
                    admin-state enable
                }
            }
        }

    The algorithm determines which lines are containers (have children at a deeper
    indentation level) and which are leaves (no children), then emits braces accordingly.
    """
    input_lines = text.splitlines()
    if not input_lines:
        return ""

    # Parse lines into (indent_level, text) tuples
    parsed = []
    for line in input_lines:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        parsed.append((indent, line.strip()))

    if not parsed:
        return ""

    output_lines = []
    indent_stack = []  # Stack of indent levels for open braces

    for i, (indent, line_text) in enumerate(parsed):
        # Close any open braces for sections that are at or deeper than current indent
        while indent_stack and indent_stack[-1] >= indent:
            indent_stack.pop()
            output_lines.append(INDENT * len(indent_stack) + "}")

        # Determine if this line is a container (has children at deeper indent)
        is_container = False
        if i + 1 < len(parsed):
            next_indent = parsed[i + 1][0]
            if next_indent > indent:
                is_container = True

        if is_container:
            output_lines.append(INDENT * len(indent_stack) + line_text + " {")
            indent_stack.append(indent)
        else:
            output_lines.append(INDENT * len(indent_stack) + line_text)

    # Close remaining open braces
    while indent_stack:
        indent_stack.pop()
        output_lines.append(INDENT * len(indent_stack) + "}")

    return "\n".join(output_lines)


def get_sros_remediation(name: str, actual_config: str, rendered_config: str) -> str:
    """Generate Nokia SROS MD-CLI remediation commands.

    Takes running and intended configurations in MD-CLI brace format,
    computes the diff using hier_config, and returns hierarchical MD-CLI
    patch commands wrapped in configure { ... } blocks.

    Args:
        name: Device hostname.
        actual_config: Current running configuration (MD-CLI format).
        rendered_config: Intended/desired configuration (MD-CLI format).

    Returns:
        Hierarchical MD-CLI patch commands, or empty string if no diff.

    Raises:
        ValueError: If the configuration cannot be parsed.
    """
    actual_indented = _braces_to_indented(actual_config)
    rendered_indented = _braces_to_indented(rendered_config)

    try:
        host = Host(hostname=name, os="sros", hconfig_options=SROS_OPTIONS)
        host.load_running_config(config_text=actual_indented)
        host.load_generated_config(config_text=rendered_indented)
    except (ValueError, AssertionError) as e:
        raise ValueError(f"Failed to parse SROS configuration for {name}: {e}") from e

    indented_output = host.remediation_config_filtered_text(include_tags={}, exclude_tags={})
    if not indented_output.strip():
        return ""

    return _indented_to_braces(indented_output)
