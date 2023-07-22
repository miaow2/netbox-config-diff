import traceback
from dataclasses import dataclass

from scrapli import AsyncScrapli

from netbox_config_diff.choices import ConfigComplianceStatusChoices


@dataclass
class DeviceDataClass:
    pk: int
    name: str
    mgmt_ip: str
    platform: str
    command: str
    exclude_regex: str
    username: str
    password: str
    rendered_config: str | None = None
    actual_config: str | None = None
    diff: str | None = None
    error: str | None = None
    auth_strict_key: bool = False
    transport: str = "asyncssh"

    def __str__(self):
        return self.name

    def to_scrapli(self):
        return {
            "host": self.mgmt_ip,
            "auth_username": self.username,
            "auth_password": self.password,
            "platform": self.platform,
            "auth_strict_key": self.auth_strict_key,
            "transport": self.transport,
        }

    def to_db(self):
        if self.error:
            status = ConfigComplianceStatusChoices.ERRORED
        elif self.diff:
            status = ConfigComplianceStatusChoices.FAILED
        else:
            status = ConfigComplianceStatusChoices.COMPLIANT

        return {
            "device_id": self.pk,
            "status": status,
            "diff": self.diff or "",
            "error": self.error or "",
            "rendered_config": self.rendered_config or "",
            "actual_config": self.actual_config or "",
        }

    async def get_actual_config(self):
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
