from datetime import datetime
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.filters import ChangeLoggedModelFilter, NetBoxModelFilter, PrimaryModelFilter
from strawberry.scalars import ID
from strawberry_django import DatetimeFilterLookup

from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute

if TYPE_CHECKING:
    from dcim.graphql.filters import DeviceFilter, PlatformFilter
    from users.graphql.filters import UserFilter

    from .enums import ConfigComplianceStatusEnum, ConfigurationRequestStatusEnum


@strawberry_django.filter_type(ConfigCompliance, lookups=True)
class ConfigComplianceFilter(ChangeLoggedModelFilter):
    device: Annotated["DeviceFilter", strawberry.lazy("dcim.graphql.filters")] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()
    status: Annotated["ConfigComplianceStatusEnum", strawberry.lazy("netbox_config_diff.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    diff: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    error: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    actual_config: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    rendered_config: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    missing: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    extra: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    patch: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(ConfigurationRequest, lookups=True)
class ConfigurationRequestFilter(PrimaryModelFilter):
    description: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated["ConfigurationRequestStatusEnum", strawberry.lazy("netbox_config_diff.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    devices: Annotated["DeviceFilter", strawberry.lazy("dcim.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    created_by: Annotated["UserFilter", strawberry.lazy("users.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    created_by_id: ID | None = strawberry_django.filter_field()
    approved_by: Annotated["UserFilter", strawberry.lazy("users.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    approved_by_id: ID | None = strawberry_django.filter_field()
    scheduled_by: Annotated["UserFilter", strawberry.lazy("users.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    scheduled_by_id: ID | None = strawberry_django.filter_field()
    scheduled: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    started: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    completed: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()


@strawberry_django.filter(PlatformSetting, lookups=True)
class PlatformSettingFilter(NetBoxModelFilter):
    platform: Annotated["PlatformFilter", strawberry.lazy("dcim.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    platform_id: ID | None = strawberry_django.filter_field()
    driver: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    description: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    command: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    exclude_regex: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(Substitute, lookups=True)
class SubstituteFilter(NetBoxModelFilter):
    platform_setting: (
        Annotated["PlatformSettingFilter", strawberry.lazy("netbox_config_diff.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    platform_setting_id: ID | None = strawberry_django.filter_field()
    name: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    description: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
    regexp: strawberry_django.FilterLookup[str] | None = strawberry_django.filter_field()
