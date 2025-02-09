import strawberry
import strawberry_django

from netbox_config_diff.graphql.types import (
    ConfigComplianceType,
    ConfigurationRequestType,
    PlatformSettingType,
    SubstituteType,
)
from netbox_config_diff.models import ConfigCompliance, ConfigurationRequest, PlatformSetting, Substitute


@strawberry.type
class NetBoxConfigDiffQuery:
    @strawberry.field
    def config_compliance(self, id: int) -> ConfigComplianceType:
        return ConfigCompliance.objects.get(pk=id)

    config_compliance_list: list[ConfigComplianceType] = strawberry_django.field()

    @strawberry.field
    def configuration_request(self, id: int) -> ConfigurationRequestType:
        return ConfigurationRequest.objects.get(pk=id)

    configuration_request_list: list[ConfigurationRequestType] = strawberry_django.field()

    @strawberry.field
    def platform_setting(self, id: int) -> PlatformSettingType:
        return PlatformSetting.objects.get(pk=id)

    platform_setting_list: list[PlatformSettingType] = strawberry_django.field()

    @strawberry.field
    def substitute(self, id: int) -> SubstituteType:
        return Substitute.objects.get(pk=id)

    substitute_list: list[SubstituteType] = strawberry_django.field()


schema = [NetBoxConfigDiffQuery]
