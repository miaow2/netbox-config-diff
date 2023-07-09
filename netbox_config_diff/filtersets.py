import django_filters
from dcim.models import Platform
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from . import models


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
        model = models.PlatformSetting
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
