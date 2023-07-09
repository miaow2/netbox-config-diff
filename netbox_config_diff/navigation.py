from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

plugin_buttons = [
    PluginMenuButton(
        link="plugins:netbox_config_diff:platformsetting_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    )
]

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_config_diff:platformsetting_list",
        link_text="Platform Settings",
        buttons=plugin_buttons,
    ),
)
