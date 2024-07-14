import strawberry_django
from netbox.graphql.filter_mixins import BaseFilterMixin, autotype_decorator

from netbox_config_diff.filtersets import (
    ConfigComplianceFilterSet,
    ConfigurationRequestFilterSet,
    PlatformSettingFilterSet,
    SubstituteFilterSet,
)
from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute


@strawberry_django.filter(ConfigCompliance, lookups=True)
@autotype_decorator(ConfigComplianceFilterSet)
class ConfigComplianceFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(ConfigurationRequest, lookups=True)
@autotype_decorator(ConfigurationRequestFilterSet)
class ConfigurationRequestFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(PlatformSetting, lookups=True)
@autotype_decorator(PlatformSettingFilterSet)
class PlatformSettingFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(Substitute, lookups=True)
@autotype_decorator(SubstituteFilterSet)
class SubstituteFilter(BaseFilterMixin):
    pass
