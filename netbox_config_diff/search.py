from netbox.search import SearchIndex, register_search

from netbox_config_diff import models


@register_search
class PlatformSettingIndex(SearchIndex):
    model = models.PlatformSetting
    fields = (
        ("driver", 100),
        ("command", 500),
        ("exclude_regex", 1000),
    )


@register_search
class ConfigurationRequestIndex(SearchIndex):
    model = models.ConfigurationRequest
    fields = (
        ("description", 100),
        ("comments", 500),
    )


@register_search
class SubstituteIndex(SearchIndex):
    model = models.Substitute
    fields = (
        ("name", 100),
        ("description", 500),
        ("regexp", 1000),
    )
