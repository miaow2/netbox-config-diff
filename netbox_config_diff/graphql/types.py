from typing import Annotated

import strawberry
import strawberry_django
from dcim.graphql.types import DeviceType, PlatformType
from netbox.graphql.types import NetBoxObjectType, ObjectType
from users.graphql.types import UserType

from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute


@strawberry_django.type(ConfigCompliance, fields="__all__")
class ConfigComplianceType(ObjectType):
    device: Annotated["DeviceType", strawberry.lazy("dcim.graphql.types")]
    status: str
    diff: str
    error: str
    actual_config: str
    rendered_config: str
    missing: str
    extra: str
    patch: str


@strawberry_django.type(ConfigurationRequest, fields="__all__")
class ConfigurationRequestType(NetBoxObjectType):
    created_by: Annotated["UserType", strawberry.lazy("users.graphql.types")] | None
    approved_by: Annotated["UserType", strawberry.lazy("users.graphql.types")] | None
    scheduled_by: Annotated["UserType", strawberry.lazy("users.graphql.types")] | None
    status: str
    devices: list[Annotated["DeviceType", strawberry.lazy("dcim.graphql.types")]]
    description: str
    comments: str
    scheduled: str
    started: str
    completed: str


@strawberry_django.type(PlatformSetting, fields="__all__")
class PlatformSettingType(NetBoxObjectType):
    platform: Annotated["PlatformType", strawberry.lazy("dcim.graphql.types")]
    description: str
    driver: str
    command: str
    exclude_regex: str


@strawberry_django.type(Substitute, fields="__all__")
class SubstituteType(NetBoxObjectType):
    platform_setting: Annotated["PlatformSettingType", strawberry.lazy("netbox_config_diff.graphql.types")]
    name: str
    description: str
    regexp: str
