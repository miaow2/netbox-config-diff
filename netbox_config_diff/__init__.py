from extras.plugins import PluginConfig

__version__ = "0.1.0"


class ConfigDiffConfig(PluginConfig):
    name = "netbox_config_diff"
    verbose_name = "NetBox Config Diff Plugin"
    description = "Find diff between the intended device configuration and actual."
    author = "Artem Kotik"
    email = "miaow2@yandex.ru"
    version = __version__
    base_url = "config-diff"


config = ConfigDiffConfig
