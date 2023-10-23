from dcim.api.serializers import NestedDeviceSerializer, NestedPlatformSerializer
from dcim.models import Device
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from users.api.nested_serializers import NestedUserSerializer
from utilities.utils import local_now

from netbox_config_diff.choices import ConfigComplianceStatusChoices, ConfigurationRequestStatusChoices
from netbox_config_diff.constants import ACCEPTABLE_DRIVERS
from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute


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
            "missing",
            "extra",
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
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )


class NestedPlatformSettingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_config_diff-api:platformsetting-detail")

    class Meta:
        model = PlatformSetting
        fields = ("id", "url", "display", "driver")


class ConfigurationRequestSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_config_diff-api:configurationrequest-detail"
    )
    devices = SerializedPKRelatedField(
        queryset=Device.objects.all(),
        serializer=NestedDeviceSerializer,
        many=True,
    )
    status = ChoiceField(choices=ConfigurationRequestStatusChoices, read_only=True)
    created_by = NestedUserSerializer(read_only=True)
    approved_by = NestedUserSerializer(read_only=True)
    scheduled_by = NestedUserSerializer(read_only=True)

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
    created_by = NestedUserSerializer()


class NestedConfigurationRequestSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_config_diff-api:configurationrequest-detail"
    )
    status = ChoiceField(choices=ConfigurationRequestStatusChoices)

    class Meta:
        model = ConfigurationRequest
        fields = ("id", "url", "display", "status")


class ConfigurationRequestScheduleSerializer(serializers.Serializer):
    schedule_at = serializers.DateTimeField()

    def validate_schedule_at(self, value):
        if value < local_now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value


class SubstituteSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_config_diff-api:substitute-detail")
    platform_setting = NestedPlatformSettingSerializer()

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
