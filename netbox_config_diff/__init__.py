from netbox.plugins import PluginConfig

__author__ = "Artem Kotik"
__email__ = "miaow2@yandex.ru"
__version__ = "2.10.0"


class ConfigDiffConfig(PluginConfig):
    name = "netbox_config_diff"
    verbose_name = "NetBox Config Diff Plugin"
    description = "Find diff and push rendered device configurations from NetBox to devices and apply them."
    author = __author__
    author_email = __email__
    version = __version__
    base_url = "config-diff"
    required_settings = ["USERNAME", "PASSWORD"]
    min_version = "4.1.0"
    default_settings = {
        "USER_SECRET_ROLE": "Username",
        "PASSWORD_SECRET_ROLE": "Password",
        "SECOND_AUTH_SECRET_ROLE": "Second Auth",
    }


config = ConfigDiffConfig
