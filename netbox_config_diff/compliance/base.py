import asyncio
import re
import traceback
from typing import Iterable, Iterator

from core.choices import DataSourceStatusChoices
from core.models import DataFile, DataSource
from dcim.choices import DeviceStatusChoices
from dcim.models import Device, Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from extras.scripts import MultiObjectVar, ObjectVar
from jinja2.exceptions import TemplateError
from netutils.config.compliance import diff_network_config
from utilities.exceptions import AbortScript

from netbox_config_diff.models import ConfigCompliance

from .models import DeviceDataClass
from .secrets import SecretsMixin
from .utils import PLATFORM_MAPPING, exclude_lines, get_unified_diff


class ConfigDiffBase(SecretsMixin):
    site = ObjectVar(
        model=Site,
        required=False,
        description="Run compliance for devices (with status Active, "
        "primary IP, platform and config template) in this site",
    )
    devices = MultiObjectVar(
        model=Device,
        required=False,
        query_params={
            "status": DeviceStatusChoices.STATUS_ACTIVE,
            "has_primary_ip": True,
            "platform_id__n": "null",
            "config_template_id__n": "null",
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

    def validate_data(self, data: dict) -> Iterable[Device]:
        if not data["site"] and not data["devices"]:
            raise AbortScript("Define site or devices")
        if data.get("data_source") and data["data_source"].status != DataSourceStatusChoices.COMPLETED:
            raise AbortScript("Define synced DataSource")

        self.data = data
        if data["devices"]:
            devices = (
                data["devices"]
                .filter(
                    status=DeviceStatusChoices.STATUS_ACTIVE,
                    platform__platform_setting__isnull=False,
                    config_template__isnull=False,
                )
                .exclude(
                    Q(primary_ip4__isnull=True) & Q(primary_ip6__isnull=True),
                )
            )
        else:
            devices = Device.objects.filter(
                site=data["site"],
                status=DeviceStatusChoices.STATUS_ACTIVE,
                platform__platform_setting__isnull=False,
                config_template__isnull=False,
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

    def get_devices_with_rendered_configs(self, devices: Iterable[Device]) -> Iterator[DeviceDataClass]:
        self.check_netbox_secrets()
        self.substitutes = {}
        for device in devices:
            username, password = self.get_credentials(device)
            rendered_config = None
            error = None
            context_data = device.get_config_context()
            context_data.update({"device": device})
            if config_template := device.get_config_template():
                try:
                    rendered_config = config_template.render(context=context_data)
                    rendered_config = re.sub(r"{{.+}}\s+", "", rendered_config)
                except TemplateError:
                    error = traceback.format_exc()
            else:
                error = "Define config template for device"

            platform = device.platform.platform_setting.driver
            if not self.substitutes.get(platform):
                if substitutes := device.platform.platform_setting.substitutes.all():
                    self.substitutes[platform] = [s.regexp for s in substitutes]

            yield DeviceDataClass(
                pk=device.pk,
                name=device.name,
                mgmt_ip=str(device.primary_ip.address.ip),
                platform=platform,
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
            cleaned_config = exclude_lines(device.actual_config, device.exclude_regex.splitlines())
            if self.substitutes.get(device.platform):
                cleaned_config = exclude_lines(cleaned_config, self.substitutes[device.platform])
            device.diff = get_unified_diff(device.rendered_config, cleaned_config, device.name)
            if device.platform in PLATFORM_MAPPING:
                device.missing = diff_network_config(
                    device.rendered_config, cleaned_config, PLATFORM_MAPPING[device.platform]
                )
                device.extra = diff_network_config(
                    cleaned_config, device.rendered_config, PLATFORM_MAPPING[device.platform]
                )
