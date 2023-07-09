import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from . import models


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
        model = models.PlatformSetting
        fields = ("driver", "platform", "command", "description", "exclude_regex", "tags", "created", "last_updated")
        default_columns = ("driver", "platform", "command", "description", "exclude_regex")
