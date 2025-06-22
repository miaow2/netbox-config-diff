# TODO: After drop 4.2 support write all graphql filters
# import strawberry_django
# import strawberry
# from strawberry.scalars import ID
# from core.graphql.filter_mixins import BaseFilterMixin, BaseObjectTypeFilterMixin, ChangeLogFilterMixin
# from typing import Annotated, TYPE_CHECKING


# from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute
# if TYPE_CHECKING:
#     from .enums import ConfigComplianceStatusEnum, ConfigurationRequestStatusEnum
#     from dcim.graphql.filters import DeviceFilter

# @strawberry_django.filter_type(ConfigCompliance, lookups=True)
# class ConfigComplianceFilter(BaseFilterMixin):
#     device = Annotated["DeviceFilter", strawberry.lazy("dcim.graphql.filters")] | None = (
#         strawberry_django.filter_field()
#     )
#     device_id: ID | None = strawberry_django.filter_field()
#     status: Annotated["ConfigComplianceStatusEnum", strawberry.lazy("dcim.graphql.enums")] | None = (
#         strawberry_django.filter_field()
#     )
#     diff: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
#     error: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
#     actual_config: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
#     rendered_config: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
#     missing: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
#     extra: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
#     patch: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()


# @strawberry_django.filter(ConfigurationRequest, lookups=True)
# @autotype_decorator(ConfigurationRequestFilterSet)
# class ConfigurationRequestFilter(BaseFilterMixin):
#     pass


# @strawberry_django.filter(PlatformSetting, lookups=True)
# @autotype_decorator(PlatformSettingFilterSet)
# class PlatformSettingFilter(BaseFilterMixin):
#     pass


# @strawberry_django.filter(Substitute, lookups=True)
# @autotype_decorator(SubstituteFilterSet)
# class SubstituteFilter(BaseFilterMixin):
#     pass
