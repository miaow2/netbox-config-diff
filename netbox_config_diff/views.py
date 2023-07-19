from netbox.views import generic
from utilities.views import register_model_view

from .filtersets import ConfigComplianceFilterSet, PlatformSettingFilterSet
from .forms import (
    ConfigComplianceFilterForm,
    PlatformSettingBulkEditForm,
    PlatformSettingFilterForm,
    PlatformSettingForm,
)
from .models import ConfigCompliance, PlatformSetting
from .tables import ConfigComplianceTable, PlatformSettingTable


@register_model_view(ConfigCompliance)
class ConfigComplianceView(generic.ObjectView):
    queryset = ConfigCompliance.objects.all()


class ConfigComplianceListView(generic.ObjectListView):
    queryset = ConfigCompliance.objects.prefetch_related("device")
    filterset = ConfigComplianceFilterSet
    filterset_form = ConfigComplianceFilterForm
    table = ConfigComplianceTable


@register_model_view(ConfigCompliance, "delete")
class ConfigComplianceDeleteView(generic.ObjectDeleteView):
    queryset = ConfigCompliance.objects.all()


class ConfigComplianceBulkDeleteView(generic.BulkDeleteView):
    queryset = ConfigCompliance.objects.all()
    filterset = ConfigComplianceFilterSet
    table = ConfigComplianceTable


@register_model_view(PlatformSetting)
class PlatformSettingView(generic.ObjectView):
    queryset = PlatformSetting.objects.all()


class PlatformSettingListView(generic.ObjectListView):
    queryset = PlatformSetting.objects.prefetch_related("platform", "tags")
    filterset = PlatformSettingFilterSet
    filterset_form = PlatformSettingFilterForm
    table = PlatformSettingTable


@register_model_view(PlatformSetting, "edit")
class PlatformSettingEditView(generic.ObjectEditView):
    queryset = PlatformSetting.objects.all()
    form = PlatformSettingForm


@register_model_view(PlatformSetting, "delete")
class PlatformSettingDeleteView(generic.ObjectDeleteView):
    queryset = PlatformSetting.objects.all()


class PlatformSettingBulkEditView(generic.BulkEditView):
    queryset = PlatformSetting.objects.all()
    filterset = PlatformSettingFilterSet
    table = PlatformSettingTable
    form = PlatformSettingBulkEditForm


class PlatformSettingBulkDeleteView(generic.BulkDeleteView):
    queryset = PlatformSetting.objects.all()
    filterset = PlatformSettingFilterSet
    table = PlatformSettingTable
