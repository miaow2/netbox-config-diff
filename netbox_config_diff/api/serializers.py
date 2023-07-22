from dcim.api.serializers import NestedDeviceSerializer, NestedPlatformSerializer
from netbox.api.fields import ChoiceField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from netbox_config_diff.choices import ConfigComplianceStatusChoices
from netbox_config_diff.models import ConfigCompliance, PlatformSetting


class ConfigComplianceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_config_diff-api:configcompliance-detail")
    device = NestedDeviceSerializer()
    status = ChoiceField(choices=ConfigComplianceStatusChoices)

    class Meta:
        model = ConfigCompliance
        fields = (
            "id",
            "url",
            "display",
            "device",
            "status",
            "error",
            "diff",
            "rendered_config",
            "actual_config",
            "created",
            "last_updated",
        )


class PlatformSettingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_config_diff-api:platformsetting-detail")
    platform = NestedPlatformSerializer()

    class Meta:
        model = PlatformSetting
        fields = (
            "id",
            "url",
            "display",
            "platform",
            "driver",
            "command",
            "exclude_regex",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
