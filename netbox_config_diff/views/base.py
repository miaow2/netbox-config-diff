from django.urls import reverse
from netbox.views.generic import ObjectDeleteView, ObjectEditView


class BaseObjectDeleteView(ObjectDeleteView):
    def get_return_url(self, request, obj=None):
        return reverse(f"plugins:netbox_config_diff:{self.queryset.model._meta.model_name}_list")


class BaseObjectEditView(ObjectEditView):
    @property
    def default_return_url(self) -> str:
        return f"plugins:netbox_config_diff:{self.queryset.model._meta.model_name}_list"
