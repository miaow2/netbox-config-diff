from extras.plugins import PluginMenu, PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices


def get_add_button(model: str) -> PluginMenuButton:
    return PluginMenuButton(
        link=f"plugins:netbox_config_diff:{model}_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
        permissions=[f"netbox_config_diff.add_{model}"],
    )


def get_menu_item(model: str, verbose_name: str, add_button: bool = True) -> PluginMenuItem:
    return PluginMenuItem(
        link=f"plugins:netbox_config_diff:{model}_list",
        link_text=verbose_name,
        buttons=[get_add_button(model)] if add_button else [],
        permissions=[f"netbox_config_diff.view_{model}"],
    )


compliance_items = (
    get_menu_item("platformsetting", "Platform Settings"),
    get_menu_item("configcompliance", "Config Compliances", add_button=False),
)

config_items = (
    get_menu_item("configurationrequest", "Configuration Requests"),
    get_menu_item("substitute", "Substitutes"),
    PluginMenuItem(
        link="plugins:netbox_config_diff:configurationrequest_job_list",
        link_text="Jobs",
        buttons=[],
        permissions=["core.view_job"],
    ),
)

menu = PluginMenu(
    label="Config Diff Plugin",
    groups=(
        ("Compliance", compliance_items),
        ("Config Management", config_items),
    ),
    icon_class="mdi mdi-vector-difference",
)
