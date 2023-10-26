import asyncio
import re
import traceback
from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable

from asgiref.sync import sync_to_async
from dcim.models import Device
from jinja2.exceptions import TemplateError
from netutils.config.compliance import diff_network_config
from scrapli import AsyncScrapli
from scrapli_cfg.platform.base.async_platform import AsyncScrapliCfgPlatform
from scrapli_cfg.response import ScrapliCfgResponse
from utilities.utils import NetBoxFakeRequest

from netbox_config_diff.compliance.secrets import SecretsMixin
from netbox_config_diff.compliance.utils import PLATFORM_MAPPING, get_unified_diff
from netbox_config_diff.configurator.exceptions import DeviceConfigurationError, DeviceValidationError
from netbox_config_diff.configurator.utils import CustomLogger
from netbox_config_diff.constants import ACCEPTABLE_DRIVERS
from netbox_config_diff.models import ConfiguratorDeviceDataClass

from .factory import AsyncScrapliCfg


class Configurator(SecretsMixin):
    def __init__(self, devices: Iterable[Device], request: NetBoxFakeRequest) -> None:
        self.devices = devices
        self.request = request
        self.unprocessed_devices: set[ConfiguratorDeviceDataClass] = set()
        self.processed_devices: set[ConfiguratorDeviceDataClass] = set()
        self.failed_devices: set[ConfiguratorDeviceDataClass] = set()
        self.substitutes: dict[str, list] = {}
        self.logger = CustomLogger()
        self.connections: dict[str, AsyncScrapliCfgPlatform] = {}

    def validate_devices(self) -> None:
        self.check_netbox_secrets()
        for device in self.devices:
            username, password, auth_secondary = self.get_credentials(device)
            if device.platform.platform_setting is None:
                self.logger.log_warning(f"Skipping {device}, add PlatformSetting for {device.platform} platform")
            elif device.platform.platform_setting.driver not in ACCEPTABLE_DRIVERS:
                self.logger.log_warning(
                    f"Skipping {device}, driver {device.platform.platform_setting.driver} is not supported"
                )
            else:
                rendered_config = None
                error = None
                context_data = device.get_config_context()
                context_data.update({"device": device})
                if config_template := device.get_config_template():
                    try:
                        rendered_config = config_template.render(context=context_data)
                    except TemplateError:
                        error = traceback.format_exc()
                        self.logger.log_failure(error)
                else:
                    error = "Define config template for device"
                    self.logger.log_failure(error)

                d = ConfiguratorDeviceDataClass(
                    pk=device.pk,
                    name=device.name,
                    mgmt_ip=str(device.primary_ip.address.ip),
                    platform=device.platform.platform_setting.driver,
                    username=username,
                    password=password,
                    auth_secondary=auth_secondary,
                    rendered_config=rendered_config,
                    error=error,
                )
                if error:
                    self.failed_devices.add(d)
                else:
                    self.connections[d.name] = AsyncScrapliCfg(
                        conn=AsyncScrapli(**d.to_scrapli()), dedicated_connection=True
                    )
                    self.unprocessed_devices.add(d)
                    if not self.substitutes.get(d.platform):
                        if substitutes := device.platform.platform_setting.substitutes.all():
                            self.substitutes[d.platform] = [
                                (s.name, re.compile(s.regexp, flags=re.I | re.M)) for s in substitutes
                            ]

        if self.failed_devices:
            raise DeviceValidationError(
                "Error in validating devices", devices=", ".join(f"{d.name}: {d.error}" for d in self.failed_devices)
            )

        self.logger.log_info(f"Working with {', '.join(d.name for d in self.unprocessed_devices)}")

    @asynccontextmanager
    async def connection(self, only_processed_devices: bool = False) -> AsyncIterator[None]:
        if only_processed_devices:
            connections = [self.connections[device.name] for device in self.processed_devices]
        else:
            connections = self.connections.values()
        try:
            await asyncio.gather(*(conn.__aenter__() for conn in connections))
            yield
        finally:
            await asyncio.gather(*(conn.__aexit__(None, None, None) for conn in connections))

    def collect_diffs(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._collect_diffs())

    @sync_to_async
    def update_diffs(self) -> None:
        for device in self.unprocessed_devices:
            device.send_to_db()

    async def _collect_diffs(self) -> None:
        async with self.connection():
            await asyncio.gather(*(self._collect_one_diff(d) for d in self.unprocessed_devices))
        await self.update_diffs()

    async def _collect_one_diff(self, device: ConfiguratorDeviceDataClass) -> None:
        self.logger.log_info(f"Collecting diff on {device.name}")
        try:
            conn = self.connections[device.name]
            if substitutes := self.substitutes.get(device.platform):
                actual_config, rendered_config = await conn.render_substituted_config(
                    config_template=device.rendered_config, substitutes=substitutes
                )
                device.rendered_config = rendered_config
            else:
                actual_config = await conn.get_config()
            device.actual_config = conn.clean_config(actual_config.result)

            device.diff = get_unified_diff(device.rendered_config, device.actual_config, device.name)
            self.logger.add_diff(device.name, diff=device.diff)
            device.missing = diff_network_config(
                device.rendered_config, device.actual_config, PLATFORM_MAPPING[device.platform]
            )
            device.extra = diff_network_config(
                device.actual_config, device.rendered_config, PLATFORM_MAPPING[device.platform]
            )
            self.logger.log_info(f"Got diff from {device.name}")
        except Exception:
            error = traceback.format_exc()
            device.error = error
            self.logger.log_failure(error)
            self.logger.add_diff(device.name, error=error)

    def push_configs(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._push_configs())

    async def _push_configs(self) -> None:
        async with self.connection():
            await asyncio.gather(*(self._collect_one_diff(d) for d in self.unprocessed_devices))
            await self.update_diffs()
            await asyncio.gather(*(self._push_one_config(d) for d in self.unprocessed_devices))
        if self.failed_devices:
            self.logger.log_warning(f"Failed device(s): {', '.join(d.name for d in self.failed_devices)}")
            async with self.connection(only_processed_devices=True):
                await self.rollback()
            raise DeviceConfigurationError(
                "Error in configuring devices",
                devices=", ".join(f"{d.name}: {d.config_error}" for d in self.failed_devices),
            )

    async def _push_one_config(self, device: ConfiguratorDeviceDataClass) -> None:
        self.logger.log_info(f"Push config to {device.name}")
        try:
            conn = self.connections[device.name]
            response = await conn.load_config(config=device.rendered_config, replace=True)
            if response.failed:
                await self.abort_config("load", conn, response, device.name)
                return
            response = await conn.commit_config()
            if response.failed:
                await self.abort_config("commit", conn, response, device.name)
                return
            self.unprocessed_devices.remove(device)
            self.processed_devices.add(device)
            self.logger.log_info(f"Successfully pushed config to {device.name}")
        except Exception:
            error = traceback.format_exc()
            device.config_error = error
            self.logger.log_failure(error)
            self.unprocessed_devices.remove(device)
            self.failed_devices.add(device)

    async def abort_config(
        self,
        operation: str,
        conn: AsyncScrapliCfgPlatform,
        response: ScrapliCfgResponse,
        device: ConfiguratorDeviceDataClass,
    ) -> None:
        self.logger.log_failure(f"Failed to {operation} config on {device.name}: {response.result}")
        device.config_error = response.result
        await conn.abort_config()
        self.unprocessed_devices.remove(device)
        self.failed_devices.add(device)
        self.logger.log_info(f"Aborted config on {device.name}")

    async def rollback(self) -> None:
        self.logger.log_info(f"Rollback config: {', '.join(d.name for d in self.processed_devices)}")
        await asyncio.gather(*(self._rollback_one(d) for d in self.processed_devices))

    async def _rollback_one(self, device: ConfiguratorDeviceDataClass) -> None:
        conn = self.connections[device.name]
        await conn.load_config(config=device.actual_config, replace=True)
        await conn.commit_config()
        self.logger.log_info(f"Successfully rollbacked {device.name}")
