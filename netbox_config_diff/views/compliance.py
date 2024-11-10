from dcim.models import Device
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from netbox.settings import VERSION
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from netbox_config_diff.compliance.utils import get_diff_statistics
from netbox_config_diff.filtersets import ConfigComplianceFilterSet, PlatformSettingFilterSet
from netbox_config_diff.forms import (
    ConfigComplianceFilterForm,
    PlatformSettingBulkEditForm,
    PlatformSettingFilterForm,
    PlatformSettingForm,
)
from netbox_config_diff.models import ConfigCompliance, PlatformSetting
from netbox_config_diff.tables import ConfigComplianceTable, PlatformSettingTable

from .base import BaseConfigComplianceConfigView, BaseObjectDeleteView, BaseObjectEditView


@register_model_view(ConfigCompliance)
class ConfigComplianceView(generic.ObjectView):
    queryset = ConfigCompliance.objects.all()
    base_template = "netbox_config_diff/configcompliance.html"
    template_name = "netbox_config_diff/configcompliance/data.html"

    def get_extra_context(self, request, instance):
        statistics = None
        if instance.diff:
            statistics = get_diff_statistics(instance.diff)
        return {
            "instance": instance,
            "base_template": self.base_template,
            "version": VERSION,
            "statistics": statistics,
        }


@register_model_view(ConfigCompliance, "rendered-config")
class ConfigComplianceRenderedConfigView(BaseConfigComplianceConfigView):
    queryset = ConfigCompliance.objects.all()
    template_name = "netbox_config_diff/configcompliance/config.html"
    config_field = "rendered_config"
    template_header = "Rendered Config"
    tab = ViewTab(
        label=_(template_header),
        weight=500,
    )


@register_model_view(ConfigCompliance, "actual-config")
class ConfigComplianceActualConfigView(BaseConfigComplianceConfigView):
    queryset = ConfigCompliance.objects.all()
    template_name = "netbox_config_diff/configcompliance/config.html"
    config_field = "actual_config"
    template_header = "Actual Config"
    tab = ViewTab(
        label=_(template_header),
        weight=510,
    )


@register_model_view(ConfigCompliance, "patch")
class ConfigCompliancePatchView(BaseConfigComplianceConfigView):
    queryset = ConfigCompliance.objects.all()
    template_name = "netbox_config_diff/configcompliance/config.html"
    config_field = "patch"
    template_header = "Patch"
    tab = ViewTab(
        label=_(template_header),
        weight=515,
    )


@register_model_view(ConfigCompliance, "missing-extra")
class ConfigComplianceMissingExtraConfigView(BaseConfigComplianceConfigView):
    queryset = ConfigCompliance.objects.all()
    template_name = "netbox_config_diff/configcompliance/missing_extra.html"
    config_field = "missing"
    template_header = "Missing/Extra"
    tab = ViewTab(
        label=_(template_header),
        weight=520,
    )


@register_model_view(Device, "config_compliance", "config-compliance")
class ConfigComplianceDeviceView(generic.ObjectView):
    queryset = Device.objects.all()
    base_template = "dcim/device/base.html"
    template_name = "netbox_config_diff/configcompliance/data.html"
    tab = ViewTab(
        label=_("Config Compliance"),
        weight=2110,
        badge=lambda obj: 1 if hasattr(obj, "config_compliance") else 0,
        hide_if_empty=True,
    )

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)

        if not hasattr(instance, "config_compliance"):
            return redirect("dcim:device", pk=instance.pk)

        return render(
            request,
            self.get_template_name(),
            {
                "object": instance,
                "instance": instance.config_compliance,
                "tab": self.tab,
                "base_template": self.base_template,
                **self.get_extra_context(request, instance),
            },
        )


class ConfigComplianceListView(generic.ObjectListView):
    queryset = ConfigCompliance.objects.prefetch_related("device")
    filterset = ConfigComplianceFilterSet
    filterset_form = ConfigComplianceFilterForm
    table = ConfigComplianceTable


@register_model_view(ConfigCompliance, "delete")
class ConfigComplianceDeleteView(BaseObjectDeleteView):
    queryset = ConfigCompliance.objects.all()


class ConfigComplianceBulkDeleteView(generic.BulkDeleteView):
    queryset = ConfigCompliance.objects.all()
    filterset = ConfigComplianceFilterSet
    table = ConfigComplianceTable


@register_model_view(PlatformSetting)
class PlatformSettingView(generic.ObjectView):
    queryset = PlatformSetting.objects.all()

    def get_extra_context(self, request, instance):
        return {
            "version": VERSION,
        }


class PlatformSettingListView(generic.ObjectListView):
    queryset = PlatformSetting.objects.prefetch_related("platform", "tags")
    filterset = PlatformSettingFilterSet
    filterset_form = PlatformSettingFilterForm
    table = PlatformSettingTable


@register_model_view(PlatformSetting, "edit")
class PlatformSettingEditView(BaseObjectEditView):
    queryset = PlatformSetting.objects.all()
    form = PlatformSettingForm


@register_model_view(PlatformSetting, "delete")
class PlatformSettingDeleteView(BaseObjectDeleteView):
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
