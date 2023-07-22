from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from netbox.models import NetBoxModel
from netbox.models.features import ChangeLoggingMixin
from utilities.querysets import RestrictedQuerySet

from .choices import ConfigComplianceStatusChoices


class ConfigCompliance(ChangeLoggingMixin, models.Model):
    device = models.OneToOneField(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="config_compliamce",
    )
    status = models.CharField(
        max_length=50,
        choices=ConfigComplianceStatusChoices,
        default=ConfigComplianceStatusChoices.PENDING,
    )
    diff = models.TextField(
        blank=True,
    )
    error = models.TextField(
        blank=True,
    )
    actual_config = models.TextField(
        blank=True,
    )
    rendered_config = models.TextField(
        blank=True,
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ("device",)

    def __str__(self):
        return self.device.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_config_diff:configcompliance", args=[self.pk])

    def get_status_color(self):
        return ConfigComplianceStatusChoices.colors.get(self.status)

    def update(self, commit=False, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            self.save()


class PlatformSetting(NetBoxModel):
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    platform = models.OneToOneField(
        to="dcim.Platform",
        on_delete=models.CASCADE,
        related_name="platform_setting",
    )
    driver = models.CharField(
        max_length=25,
        help_text=_(
            "Scrapli driver for platfrom, you can find them in "
            "<a href='https://github.com/carlmontanari/scrapli'>Scrapli</a> and "
            "<a href='https://github.com/scrapli/scrapli_community'>Scrapli community</a> documentation."
        ),
    )
    command = models.CharField(
        max_length=50,
        help_text=_("Command for getting config from device."),
    )
    exclude_regex = models.TextField(
        blank=True,
        help_text=_("Regex patterns to exclude from actual config, specify each pattern on a new line."),
    )

    prerequisite_models = ("dcim.Platform",)

    class Meta:
        ordering = ("driver",)

    def __str__(self):
        return f"{self.platform} {self.driver}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_config_diff:platformsetting", args=[self.pk])
