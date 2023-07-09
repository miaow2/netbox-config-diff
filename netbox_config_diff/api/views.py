from netbox.api.viewsets import NetBoxModelViewSet

from netbox_config_diff import filtersets, models

from .serializers import PlatformSettingSerializer


class PlatformSettingViewSet(NetBoxModelViewSet):
    queryset = models.PlatformSetting.objects.prefetch_related("platform", "tags")
    serializer_class = PlatformSettingSerializer
    filterset_class = filtersets.PlatformSettingFilterSet
