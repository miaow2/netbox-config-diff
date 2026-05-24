import base64
from operator import attrgetter
from typing import TYPE_CHECKING

from dcim.models import Device

if TYPE_CHECKING:
    from netbox_secrets.models import Secret

from netbox.plugins import get_installed_plugins, get_plugin_config


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
                if getattr(self.logger, "log_failure"):
                    self.logger.log_failure(f"Can't fetch master_key: {str(e)}")
                else:
                    self.logger.error(f"Can't fetch master_key: {str(e)}")
            else:
                self.log_failure(f"Can't fetch master_key: {str(e)}")

    def get_secret(self, secret: "Secret") -> str | None:
        try:
            secret.decrypt(self.master_key)
        except Exception:
            return None
        return secret.plaintext

    def get_secret_value(self, objects: tuple[object | None, ...], role_name: str) -> str | None:
        for obj in objects:
            if not obj:
                continue

            secrets = getattr(obj, "secrets", None)
            if not secrets:
                continue

            if secret := secrets.filter(role__name=role_name).first():
                if value := self.get_secret(secret):
                    return value

        return None

    def get_credentials(self, device: Device) -> tuple[str, str, str, str]:
        if not self.netbox_secrets_installed or not self.secrets_precedence:
            return self.username, self.password, self.auth_secondary, self.default_desired_privilege_level

        secret_objects: list[object] = []
        for entry in self.secrets_precedence:
            if entry == "device":
                secret_objects.append(device)
                continue
            try:
                secret_objects.append(attrgetter(entry)(device))
            except AttributeError:
                    pass

        username = self.get_secret_value(secret_objects, self.user_role) or self.username
        password = self.get_secret_value(secret_objects, self.password_role) or self.password
        auth_secondary = self.get_secret_value(secret_objects, self.auth_secondary_role) or self.auth_secondary
        default_desired_privilege_level = (
            self.get_secret_value(secret_objects, self.default_desired_privilege_level_role)
            or self.default_desired_privilege_level
        )

        return username, password, auth_secondary, default_desired_privilege_level

    def check_netbox_secrets(self) -> None:
        if "netbox_secrets" in get_installed_plugins():
            self.get_master_key()
            self.user_role = get_plugin_config("netbox_config_diff", "USER_SECRET_ROLE")
            self.password_role = get_plugin_config("netbox_config_diff", "PASSWORD_SECRET_ROLE")
            self.auth_secondary_role = get_plugin_config("netbox_config_diff", "SECOND_AUTH_SECRET_ROLE")
            self.default_desired_privilege_level_role = get_plugin_config(
                "netbox_config_diff", "DEFAULT_DESIRED_PRIVILEGE_LEVEL_ROLE"
            )
            self.secrets_precedence = get_plugin_config("netbox_config_diff", "SECRETS_PRECEDENCE")
            self.netbox_secrets_installed = True

        self.username = get_plugin_config("netbox_config_diff", "USERNAME")
        self.password = get_plugin_config("netbox_config_diff", "PASSWORD")
        self.auth_secondary = get_plugin_config("netbox_config_diff", "AUTH_SECONDARY")
        self.default_desired_privilege_level = get_plugin_config(
            "netbox_config_diff", "DEFAULT_DESIRED_PRIVILEGE_LEVEL"
        )
