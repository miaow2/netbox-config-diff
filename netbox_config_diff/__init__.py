from extras.plugins import PluginConfig

__author__ = "Artem Kotik"
__email__ = "miaow2@yandex.ru"
__version__ = "1.0.0"


class ConfigDiffConfig(PluginConfig):
    name = "netbox_config_diff"
    verbose_name = "NetBox Config Diff Plugin"
    description = "Find diff between the intended device configuration and actual."
    author = __author__
    email = __email__
    version = __version__
    base_url = "config-diff"
    required_settings = ["USERNAME", "PASSWORD"]
    min_version = "3.5.0"


config = ConfigDiffConfig
