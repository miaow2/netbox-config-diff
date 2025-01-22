from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from netbox.views.generic import ObjectDeleteView, ObjectEditView, ObjectView


class BaseObjectDeleteView(ObjectDeleteView):
    def get_return_url(self, request, obj=None):
        return reverse(f"plugins:netbox_config_diff:{self.queryset.model._meta.model_name}_list")


class BaseObjectEditView(ObjectEditView):
    @property
    def default_return_url(self) -> str:
        return f"plugins:netbox_config_diff:{self.queryset.model._meta.model_name}_list"


class BaseConfigComplianceConfigView(ObjectView):
    config_field = None
    template_header = None

    def export_parts(self, name: str, lines: str, suffix: str | None = None) -> HttpResponse:
        response = HttpResponse(lines, content_type="text")
        filename = f"{name}_{suffix if suffix else self.config_field}.txt"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        context = self.get_extra_context(request, instance)

        if request.GET.get("export_rendered_config"):
            return self.export_parts(instance.device.name, context["config"])

        if request.GET.get("export_actual_config"):
            return self.export_parts(instance.device.name, context["config"])

        if request.GET.get("export_missing"):
            return self.export_parts(instance.device.name, instance.missing, "missing")

        if request.GET.get("export_extra"):
            return self.export_parts(instance.device.name, instance.extra, "extra")

        if request.GET.get("export_patch"):
            return self.export_parts(instance.device.name, context["config"])

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
            "config_field": self.config_field,
        }
