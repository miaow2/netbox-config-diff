from dcim.models import Device
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from netbox_config_diff.filtersets import ConfigComplianceFilterSet, PlatformSettingFilterSet
from netbox_config_diff.forms import (
    ConfigComplianceFilterForm,
    PlatformSettingBulkEditForm,
    PlatformSettingFilterForm,
    PlatformSettingForm,
)
from netbox_config_diff.models import ConfigCompliance, PlatformSetting
from netbox_config_diff.tables import ConfigComplianceTable, PlatformSettingTable

from .base import BaseObjectDeleteView, BaseObjectEditView


class BaseConfigComplianceConfigView(generic.ObjectView):
    config_field = None
    template_header = None

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        context = self.get_extra_context(request, instance)

        if request.GET.get("export"):
            response = HttpResponse(context["config"], content_type="text")
            filename = f"{instance.device.name}_{self.config_field}.txt"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        return render(
            request,
            self.get_template_name(),
            {
                "object": instance,
                "tab": self.tab,
                **context,
            },
        )

    def get_extra_context(self, request, instance):
        return {
            "header": self.template_header,
            "config": getattr(instance, self.config_field),
        }


@register_model_view(ConfigCompliance)
class ConfigComplianceView(generic.ObjectView):
    queryset = ConfigCompliance.objects.all()
    base_template = "netbox_config_diff/configcompliance.html"
    template_name = "netbox_config_diff/configcompliance/data.html"

    def get_extra_context(self, request, instance):
        return {
            "instance": instance,
            "base_template": self.base_template,
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


@register_model_view(ConfigCompliance, "missing-extra")
class ConfigComplianceMissingExtraConfigView(generic.ObjectView):
    queryset = ConfigCompliance.objects.all()
    template_name = "netbox_config_diff/configcompliance/missing_extra.html"
    tab = ViewTab(
        label=_("Missing/Extra"),
        weight=520,
    )

    def export_parts(self, name, lines, suffix):
        response = HttpResponse(lines, content_type="text")
        filename = f"{name}_{suffix}.txt"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        context = self.get_extra_context(request, instance)

        if request.GET.get("export_missing"):
            return self.export_parts(instance.device.name, instance.missing, "missing")

        if request.GET.get("export_extra"):
            return self.export_parts(instance.device.name, instance.extra, "extra")

        return render(
            request,
            self.get_template_name(),
            {
                "object": instance,
                "tab": self.tab,
                **context,
            },
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
