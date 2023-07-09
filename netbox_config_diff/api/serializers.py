from dcim.api.serializers import NestedPlatformSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from netbox_config_diff.models import PlatformSetting


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
