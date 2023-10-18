import django_filters
from dcim.models import Device, Platform
from django.contrib.auth import get_user_model
from django.db.models import Q
from netbox.filtersets import ChangeLoggedModelFilterSet, NetBoxModelFilterSet
from utilities.filters import MultiValueDateTimeFilter

from netbox_config_diff.choices import ConfigComplianceStatusChoices
from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute


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


class ConfigurationRequestFilterSet(NetBoxModelFilterSet):
    created_by_id = django_filters.ModelMultipleChoiceFilter(
        queryset=get_user_model().objects.all(),
    )
    created_by = django_filters.ModelMultipleChoiceFilter(
        field_name="created_by__username",
        queryset=get_user_model().objects.all(),
        to_field_name="username",
    )
    approved_by_id = django_filters.ModelMultipleChoiceFilter(
        queryset=get_user_model().objects.all(),
    )
    approved_by = django_filters.ModelMultipleChoiceFilter(
        field_name="approved_by__username",
        queryset=get_user_model().objects.all(),
        to_field_name="username",
    )
    scheduled_by_id = django_filters.ModelMultipleChoiceFilter(
        queryset=get_user_model().objects.all(),
    )
    scheduled_by = django_filters.ModelMultipleChoiceFilter(
        field_name="scheduled_by__username",
        queryset=get_user_model().objects.all(),
        to_field_name="username",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="devices",
        queryset=Device.objects.all(),
    )
    scheduled = MultiValueDateTimeFilter()
    started = MultiValueDateTimeFilter()
    completed = MultiValueDateTimeFilter()

    class Meta:
        model = ConfigurationRequest
        fields = ["id", "status", "description", "comments"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value) | Q(comments__icontains=value)
        return queryset.filter(qs_filter)


class SubstituteFilterSet(NetBoxModelFilterSet):
    platform_setting_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PlatformSetting.objects.all(),
    )

    class Meta:
        model = Substitute
        fields = ["id", "name", "description", "regexp"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value) | Q(regexp__icontains=value)
        return queryset.filter(qs_filter)
