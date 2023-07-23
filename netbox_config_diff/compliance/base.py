import asyncio
import traceback
from typing import Iterable, Iterator

from core.choices import DataSourceStatusChoices
from core.models import DataFile, DataSource
from dcim.choices import DeviceStatusChoices
from dcim.models import Device, Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from extras.plugins import get_plugin_config
from extras.querysets import ConfigContextQuerySet
from extras.scripts import MultiObjectVar, ObjectVar
from jinja2.exceptions import TemplateError
from utilities.exceptions import AbortScript

from netbox_config_diff.models import ConfigCompliance

from .models import DeviceDataClass
from .utils import exclude_lines, get_unified_diff


class ConfigDiffBase:
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
    data_source = ObjectVar(
        model=DataSource,
        required=False,
        query_params={
            "status": DataSourceStatusChoices.COMPLETED,
        },
        description="Define synced DataSource, if you want compare configs stored in it wihout connecting to devices",
    )

    def run_script(self, data: dict) -> None:
        devices = self.validate_data(data)
        devices = list(self.get_devices_with_rendered_configs(devices))
        self.get_actual_configs(devices)
        self.get_diff(devices)
        self.update_in_db(devices)

    def validate_data(self, data: dict) -> Iterable[ConfigContextQuerySet]:
        if not data["site"] and not data["devices"]:
            raise AbortScript("Define site or devices")
        if data.get("data_source") and data["data_source"].status != DataSourceStatusChoices.COMPLETED:
            raise AbortScript("Define synced DataSource")

        self.data = data
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
            self.log_info(f"Working with device(s): {', '.join(d.name for d in devices)}")
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

    def get_devices_with_rendered_configs(self, devices: Iterable[ConfigContextQuerySet]) -> Iterator[DeviceDataClass]:
        username = get_plugin_config("netbox_config_diff", "USERNAME")
        password = get_plugin_config("netbox_config_diff", "PASSWORD")
        for device in devices:
            rendered_config = None
            error = None
            context_data = device.get_config_context()
            context_data.update({"device": device})
            if config_template := device.get_config_template():
                try:
                    rendered_config = config_template.render(context=context_data)
                except TemplateError:
                    error = traceback.format_exc()
            else:
                error = "Define config template for device"

            yield DeviceDataClass(
                pk=device.pk,
                name=device.name,
                mgmt_ip=str(device.primary_ip.address.ip),
                platform=device.platform.platform_setting.driver,
                command=device.platform.platform_setting.command,
                exclude_regex=device.platform.platform_setting.exclude_regex,
                username=username,
                password=password,
                rendered_config=rendered_config,
                error=error,
            )

    def get_config_from_datasource(self, devices: list[DeviceDataClass]) -> None:
        for device in devices:
            if df := DataFile.objects.filter(source=self.data["data_source"], path__icontains=device.name).first():
                if config := df.data_as_string:
                    device.actual_config = config
                else:
                    device.error = f"Data in file {df} is broken, skiping device {device.name}"
            else:
                device.error = f"Not found file in DataSource for device {device.name}"

    def get_actual_configs(self, devices: list[DeviceDataClass]) -> None:
        if self.data["data_source"]:
            self.get_config_from_datasource(devices)
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.gather(*(d.get_actual_config() for d in devices)))

    def get_diff(self, devices: list[DeviceDataClass]) -> None:
        for device in devices:
            if device.error is not None:
                continue
            device.diff = get_unified_diff(
                device.rendered_config, exclude_lines(device.actual_config, device.exclude_regex), device.name
            )
