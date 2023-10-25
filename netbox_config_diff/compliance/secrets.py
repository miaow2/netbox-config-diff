import base64
from typing import TYPE_CHECKING

from dcim.models import Device
from extras.plugins import get_installed_plugins, get_plugin_config

if TYPE_CHECKING:
    from netbox_secrets.models import Secret


class SecretsMixin:
    username: str
    password: str
    netbox_secrets_installed: bool = False

    def get_session_key(self) -> None:
        if "netbox_secrets_sessionid" in self.request.COOKIES:
            self.session_key = base64.b64decode(self.request.COOKIES["netbox_secrets_sessionid"])
        elif "HTTP_X_SESSION_KEY" in self.request.META:
            self.session_key = base64.b64decode(self.request.META["HTTP_X_SESSION_KEY"])
        else:
            self.session_key = None

    def get_master_key(self) -> None:
        try:
            from netbox_secrets.models import SessionKey
        except ImportError:
            return

        self.master_key = None
        self.get_session_key()
        try:
            sk = SessionKey.objects.get(userkey__user=self.request.user)
            self.master_key = sk.get_master_key(self.session_key)
        except Exception as e:
            if getattr(self, "logger"):
                self.logger.log_failure(f"Can't fetch master_key: {str(e)}")
            else:
                self.log_failure(f"Can't fetch master_key: {str(e)}")

    def get_secret(self, secret: "Secret") -> str | None:
        try:
            secret.decrypt(self.master_key)
        except Exception:
            return None
        return secret.plaintext

    def get_credentials(self, device: Device) -> tuple[str, str, str]:
        if not self.netbox_secrets_installed:
            return self.username, self.password, self.auth_secondary

        if secret := device.secrets.filter(role__name=self.user_role).first():
            username = value if (value := self.get_secret(secret)) else self.username
        else:
            username = self.username
        if secret := device.secrets.filter(role__name=self.password_role).first():
            password = value if (value := self.get_secret(secret)) else self.password
        else:
            password = self.password
        if secret := device.secrets.filter(role__name=self.auth_secondary_role).first():
            auth_secondary = value if (value := self.get_secret(secret)) else self.auth_secondary
        else:
            auth_secondary = self.auth_secondary

        return username, password, auth_secondary

    def check_netbox_secrets(self) -> None:
        if "netbox_secrets" in get_installed_plugins():
            self.get_master_key()
            self.user_role = get_plugin_config("netbox_config_diff", "USER_SECRET_ROLE")
            self.password_role = get_plugin_config("netbox_config_diff", "PASSWORD_SECRET_ROLE")
            self.auth_secondary_role = get_plugin_config("netbox_config_diff", "SECOND_AUTH_SECRET_ROLE")
            self.netbox_secrets_installed = True

        self.username = get_plugin_config("netbox_config_diff", "USERNAME")
        self.password = get_plugin_config("netbox_config_diff", "PASSWORD")
        self.auth_secondary = get_plugin_config("netbox_config_diff", "AUTH_SECONDARY")
