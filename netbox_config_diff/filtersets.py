import django_filters
from dcim.models import Device, Platform
from django.db.models import Q
from netbox.filtersets import ChangeLoggedModelFilterSet, NetBoxModelFilterSet

from .choices import ConfigComplianceStatusChoices
from .models import ConfigCompliance, PlatformSetting


class ConfigComplianceFilterSet(ChangeLoggedModelFilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
    )
    status = django_filters.MultipleChoiceFilter(
        choices=ConfigComplianceStatusChoices,
        null_value=None,
    )

    class Meta:
        model = ConfigCompliance
        fields = ["id"]

    def search(self, queryset, name, value):
        return queryset.filter(diff__icontains=value) if value.strip() else queryset


class PlatformSettingFilterSet(NetBoxModelFilterSet):
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name="platform__name",
        queryset=Platform.objects.all(),
        to_field_name="name",
    )

    class Meta:
        model = PlatformSetting
        fields = ["id", "driver", "command", "description", "exclude_regex"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(driver__icontains=value)
            | Q(command__icontains=value)
            | Q(exclude_regex__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)
