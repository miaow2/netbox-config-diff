from dcim.choices import DeviceStatusChoices
from dcim.models import Device, Platform
from django import forms
from django.contrib.auth import get_user_model
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.mixins import BootstrapMixin
from utilities.forms.widgets import DateTimePicker
from utilities.utils import local_now

from netbox_config_diff.choices import ConfigComplianceStatusChoices, ConfigurationRequestStatusChoices
from netbox_config_diff.constants import ACCEPTABLE_DRIVERS
from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute


class ConfigComplianceFilterForm(NetBoxModelFilterSetForm):
    model = ConfigCompliance
    fieldsets = ((None, ("q", "device_id", "status")),)
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
    )
    status = forms.MultipleChoiceField(
        choices=ConfigComplianceStatusChoices,
        required=False,
    )


class PlatformSettingForm(NetBoxModelForm):
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
    )

    class Meta:
        model = PlatformSetting
        fields = ("platform", "driver", "description", "command", "exclude_regex", "tags")
        widgets = {
            "exclude_regex": forms.Textarea(
                attrs={
                    "rows": 5,
                    "class": "font-monospace",
                }
            ),
        }


class PlatformSettingFilterForm(NetBoxModelFilterSetForm):
    model = PlatformSetting
    fieldsets = ((None, ("q", "platform_id", "tag")),)
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label="Platform",
    )
    tag = TagFilterField(model)


class PlatformSettingBulkEditForm(NetBoxModelBulkEditForm):
    driver = forms.CharField(
        max_length=25,
        required=False,
    )
    command = forms.CharField(
        max_length=50,
        required=False,
    )
    description = forms.CharField(
        max_length=200,
        required=False,
    )
    exclude_regex = forms.CharField(
        required=False,
        widget=forms.Textarea(),
    )

    model = PlatformSetting
    fieldsets = ((None, ("driver", "command", "description", "exclude_regex")),)
    nullable_fields = ("description", "exclude_regex")


class ConfigurationRequestForm(NetBoxModelForm):
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        query_params={
            "status": DeviceStatusChoices.STATUS_ACTIVE,
            "has_primary_ip": True,
            "platform_id__n": "null",
        },
    )
    created_by = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = ConfigurationRequest
        fields = ("devices", "description", "comments", "created_by", "tags")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["devices"].disabled = True

    def clean(self):
        super().clean()

        if devices := self.cleaned_data["devices"].filter(platform__platform_setting__isnull=True):
            platforms = {d.platform.name for d in devices}
            raise forms.ValidationError({"devices": f"Assign PlatformSetting for platform(s): {', '.join(platforms)}"})

        if drivers := {
            device.platform.platform_setting.driver
            for device in self.cleaned_data["devices"]
            if device.platform.platform_setting.driver not in ACCEPTABLE_DRIVERS
        }:
            raise forms.ValidationError({"devices": f"Driver(s) not supported: {', '.join(drivers)}"})

        if devices := list(filter(lambda x: x.get_config_template() is None, self.cleaned_data["devices"])):
            raise forms.ValidationError(
                {"devices": f"Define config template for device(s): {', '.join(d.name for d in devices)}"}
            )


class ConfigurationRequestFilterForm(NetBoxModelFilterSetForm):
    model = ConfigurationRequest
    fieldsets = ((None, ("q", "created_by_id", "approved_by_id", "scheduled_by_id", "device_id", "status", "tag")),)
    created_by_id = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label="Created by",
    )
    approved_by_id = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label="Approved by",
    )
    scheduled_by_id = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label="Scheduled by",
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
    )
    status = forms.MultipleChoiceField(
        choices=ConfigurationRequestStatusChoices,
        required=False,
    )
    tag = TagFilterField(model)


class ConfigurationRequestScheduleForm(BootstrapMixin, forms.ModelForm):
    scheduled = forms.DateTimeField(
        widget=DateTimePicker(),
        label="Schedule at",
        help_text="Schedule execution of configuration request to a set time",
    )
    scheduled_by = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = ConfigurationRequest
        fields = ("scheduled", "scheduled_by", "status")
        widgets = {
            "status": forms.HiddenInput(),
        }

    def clean(self):
        scheduled_time = self.cleaned_data.get("scheduled")
        if scheduled_time and scheduled_time < local_now():
            raise forms.ValidationError("Scheduled time must be in the future.")


class SubstituteForm(NetBoxModelForm):
    platform_setting = DynamicModelChoiceField(
        queryset=PlatformSetting.objects.all(),
    )

    class Meta:
        model = Substitute
        fields = ("platform_setting", "name", "description", "regexp", "tags")


class SubstituteFilterForm(NetBoxModelFilterSetForm):
    model = Substitute
    fieldsets = ((None, ("q", "platform_setting_id", "tag")),)
    platform_setting_id = DynamicModelMultipleChoiceField(
        queryset=PlatformSetting.objects.all(),
        required=False,
    )
    tag = TagFilterField(model)
