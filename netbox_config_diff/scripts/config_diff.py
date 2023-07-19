from typing import Iterable

from dcim.choices import DeviceStatusChoices
from dcim.models import Device, Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from extras.querysets import ConfigContextQuerySet
from extras.scripts import MultiObjectVar, ObjectVar, Script
from utilities.exceptions import AbortScript

from netbox_config_diff.compliance.base import ConfigDiffBase
from netbox_config_diff.compliance.models import DeviceDataClass
from netbox_config_diff.models import ConfigCompliance


class ConfigDiffScript(ConfigDiffBase, Script):
    class Meta:
        description = "Checks for configuration difference."
        job_timeout = 600

    site = ObjectVar(
        model=Site,
        required=False,
        description="Run compliance for devices (with status Active, primary IP and platform) in this site",
    )
    devices = MultiObjectVar(
        model=Device,
        required=False,
        query_params={
            "status": DeviceStatusChoices.STATUS_ACTIVE,
            "has_primary_ip": True,
            "platform_id__n": "null",
        },
        description="If you define devices in this field, the Site field will be ignored",
    )

    def validate_data(self, data: dict) -> Iterable[ConfigContextQuerySet]:
        if not data["site"] and not data["devices"]:
            raise AbortScript("Define site or devices")

        if data["devices"]:
            devices = data["devices"].exclude(platform__platform_setting__isnull=True)
        else:
            devices = Device.objects.filter(
                site=data["site"],
                status=DeviceStatusChoices.STATUS_ACTIVE,
                platform__platform_setting__isnull=False,
            ).exclude(
                Q(primary_ip4__isnull=True) & Q(primary_ip6__isnull=True),
            )
        if data.get("devices"):
            if qs_diff := data["devices"].difference(devices):
                platforms = {d.platform.name for d in qs_diff}
                self.log_warning(f"Define PlatformSetting for platform(s) {', '.join(platforms)}")

        if not devices:
            self.log_warning(
                "No matching devices found, devices must have status `Active`, primary IP, platform and platformsetting"
            )
        else:
            self.log_info(f"Working with devices: {', '.join(d.name for d in devices)}")
        return devices

    def update_in_db(self, devices: list[DeviceDataClass]) -> None:
        for device in devices:
            self.log_results(device)
            try:
                obj = ConfigCompliance.objects.get(device_id=device.pk)
                obj.snapshot()
                obj.update(**device.to_db())
                obj.save()
            except ObjectDoesNotExist:
                ConfigCompliance.objects.create(**device.to_db())

    def log_results(self, device: DeviceDataClass) -> None:
        if device.error:
            self.log_failure(f"{device.name} errored")
        elif device.diff:
            self.log_warning(f"{device.name} has diff between intented and actual configurations")
        else:
            self.log_success(f"{device.name} no diff")

    def run(self, data: dict, commit: bool) -> None:
        devices = self.validate_data(data)
        devices = list(self.get_devices_with_rendered_configs(devices))
        self.get_actual_configs(devices)
        self.get_diff(devices)
        self.update_in_db(devices)
