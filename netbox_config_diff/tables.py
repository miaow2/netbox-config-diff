import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .models import ConfigCompliance, PlatformSetting


class ConfigComplianceTable(NetBoxTable):
    device = tables.Column(
        linkify=True,
    )
    status = columns.ChoiceFieldColumn()
    actions = columns.ActionsColumn(
        actions=("delete", "changelog"),
    )

    class Meta(NetBoxTable.Meta):
        model = ConfigCompliance
        fields = ("id", "device", "status", "created", "last_updated")
        default_columns = fields


class PlatformSettingTable(NetBoxTable):
    driver = tables.Column(
        linkify=True,
    )
    platform = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn(
        url_name="netbox_config_diff:platformsetting_list",
    )

    class Meta(NetBoxTable.Meta):
        model = PlatformSetting
        fields = ("driver", "platform", "command", "exclude_regex", "description", "tags", "created", "last_updated")
        default_columns = ("driver", "platform", "command", "exclude_regex", "description")
