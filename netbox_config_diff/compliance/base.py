import asyncio
import traceback
from typing import Iterable, Iterator

from extras.plugins import get_plugin_config
from extras.querysets import ConfigContextQuerySet
from jinja2.exceptions import TemplateError

from .models import DeviceDataClass
from .utils import get_unified_diff


class ConfigDiffBase:
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

    def get_actual_configs(self, devices: list[DeviceDataClass]) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*(d.get_actual_config() for d in devices)))

    def get_diff(self, devices: list[DeviceDataClass]) -> None:
        for device in devices:
            if device.error is not None:
                continue
            device.diff = get_unified_diff(device.rendered_config, device.actual_config, device.name)
