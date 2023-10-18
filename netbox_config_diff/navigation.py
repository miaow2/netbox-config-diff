from django import forms
from extras.dashboard.utils import register_widget
from extras.dashboard.widgets import DashboardWidget, WidgetConfigForm
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
    PluginMenuItem(
        link="plugins:netbox_config_diff:configurationrequest_list",
        link_text="Configuration Requests",
        buttons=[get_add_button("configurationrequest")],
        permissions=["netbox_config_diff.view_configurationrequest"],
    ),
    PluginMenuItem(
        link="plugins:netbox_config_diff:configurationrequest_job_list",
        link_text="Jobs",
        buttons=[],
        permissions=["core.view_job"],
    ),
    PluginMenuItem(
        link="plugins:netbox_config_diff:substitute_list",
        link_text="Substitutes",
        buttons=[get_add_button("substitute")],
        permissions=["netbox_config_diff.view_substitute"],
    ),
)


@register_widget
class ReminderWidget(DashboardWidget):
    default_title = 'Reminder'
    description = 'Add a virtual sticky note'

    class ConfigForm(WidgetConfigForm):
        content = forms.CharField(widget=forms.Textarea())

    def render(self, request):
        return self.config.get('content')
