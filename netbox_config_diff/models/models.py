import re

import django_rq
from core.models import Job
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from netbox.constants import RQ_QUEUE_DEFAULT
from netbox.models import NetBoxModel, PrimaryModel
from netbox.models.features import ChangeLoggingMixin, JobsMixin
from rq.exceptions import InvalidJobOperation
from utilities.querysets import RestrictedQuerySet
from utilities.utils import copy_safe_request

from netbox_config_diff.choices import ConfigComplianceStatusChoices, ConfigurationRequestStatusChoices

from .base import AbsoluteURLMixin


class ConfigCompliance(AbsoluteURLMixin, ChangeLoggingMixin, models.Model):
    device = models.OneToOneField(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="config_compliance",
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
    missing = models.TextField(
        blank=True,
    )
    extra = models.TextField(
        blank=True,
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ("device",)

    def __str__(self) -> str:
        return self.device.name

    def get_status_color(self) -> str:
        return ConfigComplianceStatusChoices.colors.get(self.status)

    def update(self, commit: bool = False, **kwargs) -> None:
        if commit:
            self.snapshot()
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            self.save()


class PlatformSetting(AbsoluteURLMixin, NetBoxModel):
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
            "<a href='https://carlmontanari.github.io/scrapli/user_guide/project_details/#supported-platforms'>Scrapli</a> and "  # noqa
            "<a href='https://scrapli.github.io/scrapli_community/user_guide/project_details/#supported-platforms'>Scrapli community</a> documentation."  # noqa
        ),
    )
    command = models.CharField(
        max_length=50,
        help_text=_("Command for getting config from device."),
    )
    exclude_regex = models.TextField(
        blank=True,
        help_text=_("Regex patterns to exclude config lines from actual config, specify each pattern on a new line."),
    )

    prerequisite_models = ("dcim.Platform",)

    class Meta:
        ordering = ("driver",)

    def __str__(self) -> str:
        return f"{self.platform} {self.driver}"


class ConfigurationRequest(AbsoluteURLMixin, JobsMixin, PrimaryModel):
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    approved_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    scheduled_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=30,
        choices=ConfigurationRequestStatusChoices,
        default=ConfigurationRequestStatusChoices.CREATED,
    )
    devices = models.ManyToManyField(
        to="dcim.Device",
        related_name="configuration_requests",
    )
    scheduled = models.DateTimeField(
        null=True,
        blank=True,
    )
    started = models.DateTimeField(
        null=True,
        blank=True,
    )
    completed = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        return f"CR #{self.pk}"

    def get_status_color(self) -> str:
        return ConfigurationRequestStatusChoices.colors.get(self.status)

    @property
    def finished(self) -> bool:
        return self.status in ConfigurationRequestStatusChoices.FINISHED_STATE_CHOICES

    def delete(self, *args, **kwargs) -> None:
        super().delete(*args, **kwargs)

        queue = django_rq.get_queue(RQ_QUEUE_DEFAULT)
        for result in self.jobs.all():
            if job := queue.fetch_job(str(result.job_id)):
                try:
                    job.cancel()
                except InvalidJobOperation:
                    pass

    def enqueue_job(self, request, job_name, schedule_at=None) -> Job:
        return Job.enqueue(
            import_string(f"netbox_config_diff.jobs.{job_name}"),
            name=f"{self} {job_name}",
            instance=self,
            user=request.user,
            request=copy_safe_request(request),
            schedule_at=schedule_at,
        )

    def start(self, job: Job) -> None:
        """
        Record the job's start time and update its status to "running."
        """
        if self.started is not None:
            return
        job.start()
        self.started = timezone.now()
        self.status = ConfigurationRequestStatusChoices.RUNNING
        self.save()

    def terminate(self, job: Job, status: str = ConfigurationRequestStatusChoices.COMPLETED) -> None:
        job.terminate(status=status)
        self.status = status
        self.completed = timezone.now()
        self.save()


class Substitute(AbsoluteURLMixin, NetBoxModel):
    platform_setting = models.ForeignKey(
        to="netbox_config_diff.PlatformSetting",
        on_delete=models.CASCADE,
        related_name="substitutes",
    )
    name = models.CharField(
        max_length=250,
        unique=True,
        validators=(
            RegexValidator(
                regex=r"^[a-z0-9_]+$",
                message=_("Only alphanumeric characters and underscores are allowed."),
                flags=re.IGNORECASE,
            ),
            RegexValidator(
                regex=r"__",
                message=_("Double underscores are not permitted in names."),
                flags=re.IGNORECASE,
                inverse_match=True,
            ),
        ),
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    regexp = models.CharField(
        max_length=1000,
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
