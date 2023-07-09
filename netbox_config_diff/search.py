from netbox.search import SearchIndex, register_search

from .models import PlatformSetting


@register_search
class PlatformSettingIndex(SearchIndex):
    model = PlatformSetting
    fields = (
        ("driver", 100),
        ("command", 500),
        ("exclude_regex", 1000),
    )
