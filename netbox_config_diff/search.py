from netbox.search import SearchIndex, register_search

from . import models


@register_search
class PlatformSettingIndex(SearchIndex):
    model = models.PlatformSetting
    fields = (
        ("driver", 100),
        ("command", 500),
        ("exclude_regex", 1000),
    )
