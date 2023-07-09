from netbox.views import generic
from utilities.views import register_model_view

from . import filtersets, forms, models, tables


@register_model_view(models.PlatformSetting)
class PlatformSettingView(generic.ObjectView):
    queryset = models.PlatformSetting.objects.all()


class PlatformSettingListView(generic.ObjectListView):
    queryset = models.PlatformSetting.objects.select_related("platform")
    filterset = filtersets.PlatformSettingFilterSet
    filterset_form = forms.PlatformSettingFilterForm
    table = tables.PlatformSettingTable


@register_model_view(models.PlatformSetting, "edit")
class PlatformSettingEditView(generic.ObjectEditView):
    queryset = models.PlatformSetting.objects.all()
    form = forms.PlatformSettingForm


@register_model_view(models.PlatformSetting, "delete")
class PlatformSettingDeleteView(generic.ObjectDeleteView):
    queryset = models.PlatformSetting.objects.all()


class PlatformSettingBulkEditView(generic.BulkEditView):
    queryset = models.PlatformSetting.objects.all()
    filterset = filtersets.PlatformSettingFilterSet
    table = tables.PlatformSettingTable
    form = forms.PlatformSettingBulkEditForm


class PlatformSettingBulkDeleteView(generic.BulkDeleteView):
    queryset = models.PlatformSetting.objects.all()
    filterset = filtersets.PlatformSettingFilterSet
    table = tables.PlatformSettingTable
