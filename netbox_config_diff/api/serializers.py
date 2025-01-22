from dcim.api.serializers import DeviceSerializer, PlatformSerializer
from dcim.models import Device
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from users.api.serializers import UserSerializer
from utilities.datetime import local_now

from netbox_config_diff.choices import ConfigComplianceStatusChoices, ConfigurationRequestStatusChoices
from netbox_config_diff.constants import ACCEPTABLE_DRIVERS
from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute


class ConfigComplianceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_config_diff-api:configcompliance-detail")
    device = DeviceSerializer(nested=True)
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
            "patch",
            "missing",
            "extra",
            "created",
            "last_updated",
        )


class PlatformSettingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_config_diff-api:platformsetting-detail")
    platform = PlatformSerializer(nested=True)

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
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "driver")


class ConfigurationRequestSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_config_diff-api:configurationrequest-detail"
    )
    devices = SerializedPKRelatedField(
        queryset=Device.objects.all(),
        serializer=DeviceSerializer,
        nested=True,
        many=True,
    )
    status = ChoiceField(choices=ConfigurationRequestStatusChoices, read_only=True)
    created_by = UserSerializer(read_only=True, nested=True)
    approved_by = UserSerializer(read_only=True, nested=True)
    scheduled_by = UserSerializer(read_only=True, nested=True)

    class Meta:
        model = ConfigurationRequest
        fields = (
            "id",
            "url",
            "display",
            "devices",
            "created_by",
            "approved_by",
            "scheduled_by",
            "scheduled",
            "started",
            "completed",
            "status",
            "description",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        read_only_fields = ["started", "scheduled", "completed"]
        brief_fields = ("id", "url", "display", "status")

    def validate(self, data):
        if data.get("devices"):
            if devices := data["devices"].filter(platform__platform_setting__isnull=True):
                platforms = {d.platform.name for d in devices}
                raise ValidationError({"devices": f"Assign PlatformSetting for platform(s): {', '.join(platforms)}"})

            if drivers := {
                device.platform.platform_setting.driver
                for device in data["devices"]
                if device.platform.platform_setting.driver not in ACCEPTABLE_DRIVERS
            }:
                raise ValidationError({"devices": f"Driver(s) not supported: {', '.join(drivers)}"})

            if devices := list(filter(lambda x: x.get_config_template() is None, data["devices"])):
                raise ValidationError(
                    {"devices": f"Define config template for device(s): {', '.join(d.name for d in devices)}"}
                )

        return super().validate(data)


class ConfigurationRequestRWSerializer(ConfigurationRequestSerializer):
    created_by = UserSerializer(nested=True)


class ConfigurationRequestScheduleSerializer(serializers.Serializer):
    schedule_at = serializers.DateTimeField()

    def validate_schedule_at(self, value):
        if value < local_now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value


class SubstituteSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_config_diff-api:substitute-detail")
    platform_setting = PlatformSettingSerializer(nested=True)

    class Meta:
        model = Substitute
        fields = (
            "id",
            "url",
            "display",
            "platform_setting",
            "name",
            "description",
            "regexp",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
