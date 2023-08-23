from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices


def get_add_button(model: str) -> PluginMenuButton:
    return PluginMenuButton(
        link=f"plugins:netbox_config_diff:{model}_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
        permissions=[f"netbox_config_diff.add_{model}"],
    )


menu_items = (
    PluginMenuItem(
        link="plugins:netbox_config_diff:platformsetting_list",
        link_text="Platform Settings",
        buttons=[get_add_button("platformsetting")],
        permissions=["netbox_config_diff.view_platformsetting"],
    ),
    PluginMenuItem(
        link="plugins:netbox_config_diff:configcompliance_list",
        link_text="Config Compliances",
        buttons=[],
        permissions=["netbox_config_diff.view_configcompliance"],
    ),
)
