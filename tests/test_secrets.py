from types import SimpleNamespace

from netbox_config_diff.compliance.secrets import SecretsMixin


class DummySecretsManager:
    def __init__(self, by_role: dict[str, object]) -> None:
        self.by_role = by_role

    def filter(self, **kwargs):
        return SimpleNamespace(first=lambda: self.by_role.get(kwargs["role__name"]))


class DummySecretsMixin(SecretsMixin):
    pass


def build_mixin() -> DummySecretsMixin:
    mixin = DummySecretsMixin()
    mixin.netbox_secrets_installed = True
    mixin.username = "default-user"
    mixin.password = "default-pass"
    mixin.auth_secondary = "default-secondary"
    mixin.default_desired_privilege_level = "default-priv"
    mixin.secrets_precedence = ["device", "role", "platform"]

    mixin.user_role = "user-role"
    mixin.password_role = "password-role"
    mixin.auth_secondary_role = "secondary-role"
    mixin.default_desired_privilege_level_role = "priv-role"
    return mixin


def test_get_credentials_prefers_device_then_role_then_platform() -> None:
    mixin = build_mixin()

    device = SimpleNamespace(
        secrets=DummySecretsManager(
            {
                "user-role": SimpleNamespace(value="device-user"),
            }
        ),
        role=SimpleNamespace(
            secrets=DummySecretsManager(
                {
                    "user-role": SimpleNamespace(value="role-user"),
                    "password-role": SimpleNamespace(value="role-pass"),
                }
            )
        ),
        platform=SimpleNamespace(
            secrets=DummySecretsManager(
                {
                    "user-role": SimpleNamespace(value="platform-user"),
                    "password-role": SimpleNamespace(value="platform-pass"),
                    "secondary-role": SimpleNamespace(value="platform-secondary"),
                    "priv-role": SimpleNamespace(value="platform-priv"),
                }
            )
        ),
    )
    mixin.get_secret = lambda secret: secret.value

    assert mixin.get_credentials(device) == (
        "device-user",
        "role-pass",
        "platform-secondary",
        "platform-priv",
    )


def test_get_credentials_skips_empty_secret_value() -> None:
    mixin = build_mixin()

    device = SimpleNamespace(
        secrets=DummySecretsManager(
            {
                "password-role": SimpleNamespace(value=""),
            }
        ),
        role=SimpleNamespace(
            secrets=DummySecretsManager(
                {
                    "password-role": SimpleNamespace(value="role-pass"),
                }
            )
        ),
        platform=SimpleNamespace(secrets=DummySecretsManager({})),
    )
    mixin.get_secret = lambda secret: secret.value

    username, password, auth_secondary, default_desired_privilege_level = mixin.get_credentials(device)

    assert username == "default-user"
    assert password == "role-pass"
    assert auth_secondary == "default-secondary"
    assert default_desired_privilege_level == "default-priv"


def test_get_credentials_respects_custom_precedence() -> None:
    mixin = build_mixin()

    device = SimpleNamespace(
        secrets=DummySecretsManager(
            {
                "password-role": SimpleNamespace(value="device-pass"),
            }
        ),
        role=SimpleNamespace(
            secrets=DummySecretsManager(
                {
                    "user-role": SimpleNamespace(value="role-user"),
                    "password-role": SimpleNamespace(value="role-pass"),
                }
            )
        ),
        platform=SimpleNamespace(
            secrets=DummySecretsManager(
                {
                    "user-role": SimpleNamespace(value="platform-user"),
                }
            )
        ),
    )
    mixin.get_secret = lambda secret: secret.value

    # Force precedence: platform -> device -> role
    mixin.secrets_precedence = ["platform", "device", "role"]

    assert mixin.get_credentials(device) == (
        "platform-user",
        "device-pass",
        "default-secondary",
        "default-priv",
    )
