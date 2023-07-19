from netbox.api.viewsets import NetBoxModelViewSet, NetBoxReadOnlyModelViewSet

from netbox_config_diff.filtersets import ConfigComplianceFilterSet, PlatformSettingFilterSet
from netbox_config_diff.models import ConfigCompliance, PlatformSetting

from .serializers import ConfigComplianceSerializer, PlatformSettingSerializer


class ConfigComplianceViewSet(NetBoxReadOnlyModelViewSet):
    queryset = ConfigCompliance.objects.prefetch_related("device")
    serializer_class = ConfigComplianceSerializer
    filterset_class = ConfigComplianceFilterSet


class PlatformSettingViewSet(NetBoxModelViewSet):
    queryset = PlatformSetting.objects.prefetch_related("platform", "tags")
    serializer_class = PlatformSettingSerializer
    filterset_class = PlatformSettingFilterSet
