import traceback
from dataclasses import dataclass

from dcim.models import Device
from scrapli import AsyncScrapli

from netbox_config_diff.choices import ConfigComplianceStatusChoices

from .models import ConfigCompliance


@dataclass
class BaseDeviceDataClass:
    pk: int
    name: str
    mgmt_ip: str
    platform: str
    username: str
    password: str
    exclude_regex: str | None = None
    rendered_config: str | None = None
    actual_config: str | None = None
    diff: str = ""
    missing: str | None = None
    extra: str | None = None
    error: str = ""
    config_error: str | None = None
    auth_strict_key: bool = False
    auth_secondary: str | None = None
    transport: str = "asyncssh"

    def __str__(self) -> str:
        return self.name

    def to_scrapli(self) -> dict:
        return {
            "host": self.mgmt_ip,
            "auth_username": self.username,
            "auth_password": self.password,
            "platform": self.platform,
            "auth_strict_key": self.auth_strict_key,
            "auth_secondary": self.auth_secondary,
            "transport": self.transport,
            "transport_options": {
                "asyncssh": {
                    "kex_algs": [
                        "curve25519-sha256",
                        "curve25519-sha256@libssh.org",
                        "curve448-sha512",
                        "ecdh-sha2-nistp521",
                        "ecdh-sha2-nistp384",
                        "ecdh-sha2-nistp256",
                        "ecdh-sha2-1.3.132.0.10",
                        "diffie-hellman-group-exchange-sha256",
                        "diffie-hellman-group14-sha256",
                        "diffie-hellman-group15-sha512",
                        "diffie-hellman-group16-sha512",
                        "diffie-hellman-group17-sha512",
                        "diffie-hellman-group18-sha512",
                        "diffie-hellman-group14-sha256@ssh.com",
                        "diffie-hellman-group14-sha1",
                        "rsa2048-sha256",
                        "diffie-hellman-group1-sha1",
                        "diffie-hellman-group-exchange-sha1",
                        "diffie-hellman-group-exchange-sha256",
                    ],
                    "encryption_algs": [
                        "aes256-cbc",
                        "aes192-cbc",
                        "aes128-cbc",
                        "3des-cbc",
                        "aes256-ctr",
                        "aes192-ctr",
                        "aes128-ctr",
                        "aes128-gcm@openssh.com",
                        "chacha20-poly1305@openssh.com",
                    ],
                },
            },
        }

    def get_status(self) -> str:
        if self.error:
            return ConfigComplianceStatusChoices.ERRORED
        elif self.diff:
            return ConfigComplianceStatusChoices.DIFF
        else:
            return ConfigComplianceStatusChoices.COMPLIANT

    def to_db(self) -> dict:
        status = self.get_status()

        return {
            "device_id": self.pk,
            "status": status,
            "diff": self.diff or "",
            "error": self.error or "",
            "rendered_config": self.rendered_config or "",
            "actual_config": self.actual_config or "",
            "missing": self.missing or "",
            "extra": self.extra or "",
        }

    def send_to_db(self) -> None:
        try:
            obj = ConfigCompliance.objects.get(device_id=self.pk)
            if obj.status != self.get_status():
                obj.update(commit=True, **self.to_db())
            elif obj.diff != self.diff or obj.error != self.error:
                obj.update(commit=True, **self.to_db())
        except ConfigCompliance.DoesNotExist:
            ConfigCompliance.objects.create(**self.to_db())


class ConplianceDeviceDataClass(BaseDeviceDataClass):
    command: str
    device: Device | None = None

    def __init__(self, command: str, device: Device, **kwargs) -> None:
        super().__init__(**kwargs)
        self.command = command
        self.device = device

    async def get_actual_config(self) -> None:
        if self.error is not None:
            return
        try:
            async with AsyncScrapli(**self.to_scrapli()) as conn:
                result = await conn.send_command(self.command)
                if result.failed:
                    self.error = result.result
                else:
                    self.actual_config = result.result
        except Exception:
            self.error = traceback.format_exc()


class ConfiguratorDeviceDataClass(BaseDeviceDataClass):
    def __hash__(self) -> int:
        return hash(self.name)
