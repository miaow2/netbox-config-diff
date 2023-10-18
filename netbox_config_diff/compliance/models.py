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
    username: str
    password: str
    command: str | None = None
    exclude_regex: str | None = None
    rendered_config: str | None = None
    actual_config: str | None = None
    diff: str | None = None
    missing: str | None = None
    extra: str | None = None
    error: str | None = None
    config_error: str | None = None
    auth_strict_key: bool = False
    transport: str = "asyncssh"

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def to_scrapli(self):
        return {
            "host": self.mgmt_ip,
            "auth_username": self.username,
            "auth_password": self.password,
            "platform": self.platform,
            "auth_strict_key": self.auth_strict_key,
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

    def to_db(self):
        if self.error:
            status = ConfigComplianceStatusChoices.ERRORED
        elif self.diff:
            status = ConfigComplianceStatusChoices.DIFF
        else:
            status = ConfigComplianceStatusChoices.COMPLIANT

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
