import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute


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


class ConfigurationRequestTable(NetBoxTable):
    devices = columns.ManyToManyColumn(
        linkify_item=True,
    )
    status = columns.ChoiceFieldColumn()
    scheduled = columns.DateTimeColumn()
    started = columns.DateTimeColumn()
    completed = columns.DateTimeColumn()
    tags = columns.TagColumn(
        url_name="netbox_config_diff:configurationrequest_list",
    )
    actions = columns.ActionsColumn(
        actions=("delete", "changelog"),
    )

    class Meta(NetBoxTable.Meta):
        model = ConfigurationRequest
        fields = (
            "id",
            "devices",
            "status",
            "description",
            "created_by",
            "approved_by",
            "scheduled_by",
            "scheduled",
            "started",
            "completed",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = (
            "id",
            "devices",
            "status",
            "description",
            "created_by",
            "approved_by",
            "scheduled_by",
            "scheduled",
            "started",
            "completed",
        )


class SubstituteTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    platform_setting = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn(
        url_name="netbox_config_diff:substitute_list",
    )

    class Meta(NetBoxTable.Meta):
        model = Substitute
        fields = (
            "id",
            "name",
            "platform_setting",
            "description",
            "regexp",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = (
            "name",
            "platform_setting",
            "description",
            "regexp",
            "tags",
        )
