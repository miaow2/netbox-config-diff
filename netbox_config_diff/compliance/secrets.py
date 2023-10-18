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
            self.session_key = base64.b64decode(self.request.COOKIES['netbox_secrets_sessionid'])
        elif "HTTP_X_SESSION_KEY" in self.request.META:
            self.session_key = base64.b64decode(self.request.META['HTTP_X_SESSION_KEY'])
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

    def get_credentials(self, device: Device) -> tuple[str, str]:
        if self.netbox_secrets_installed:
            if secret := device.secrets.filter(role__name=self.user_role).first():
                if value := self.get_secret(secret):
                    username = value
            if secret := device.secrets.filter(role__name=self.password_role).first():
                if value := self.get_secret(secret):
                    password = value
            return username, password

        return self.username, self.password

    def check_netbox_secrets(self) -> None:
        if "netbox_secrets" in get_installed_plugins():
            self.get_master_key()
            self.user_role = get_plugin_config("netbox_config_diff", "USER_SECRET_ROLE")
            self.password_role = get_plugin_config("netbox_config_diff", "PASSWORD_SECRET_ROLE")
            self.netbox_secrets_installed = True
        else:
            self.username = get_plugin_config("netbox_config_diff", "USERNAME")
            self.password = get_plugin_config("netbox_config_diff", "PASSWORD")
