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


class BaseExportView(ObjectView):
    def export_parts(self, name, lines, suffix):
        response = HttpResponse(lines, content_type="text")
        filename = f"{name}_{suffix}.txt"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class BaseConfigComplianceConfigView(BaseExportView):
    config_field = None
    template_header = None

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        context = self.get_extra_context(request, instance)

        if request.GET.get("export"):
            return self.export_parts(instance.device.name, context["config"], self.config_field)

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
