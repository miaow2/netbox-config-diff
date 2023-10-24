from django.db import models
from django.urls import reverse


class AbsoluteURLMixin(models.Model):
    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse(f"plugins:netbox_config_diff:{self._meta.model_name}", args=[self.pk])
