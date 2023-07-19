from dcim.models import Device, Platform
from django import forms
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)

from .choices import ConfigComplianceStatusChoices
from .models import ConfigCompliance, PlatformSetting


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
