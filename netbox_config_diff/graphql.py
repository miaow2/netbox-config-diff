from graphene import ObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from netbox_config_diff import filtersets, models


class ConfigComplianceType(NetBoxObjectType):
    class Meta:
        model = models.ConfigCompliance
        fields = "__all__"
        filterset_class = filtersets.ConfigComplianceFilterSet


class PlatformSettingType(NetBoxObjectType):
    class Meta:
        model = models.PlatformSetting
        fields = "__all__"
        filterset_class = filtersets.PlatformSettingFilterSet


class ConfigurationRequestType(NetBoxObjectType):
    class Meta:
        model = models.ConfigurationRequest
        fields = "__all__"
        filterset_class = filtersets.ConfigurationRequestFilterSet


class SubstituteType(NetBoxObjectType):
    class Meta:
        model = models.Substitute
        fields = "__all__"
        filterset_class = filtersets.SubstituteFilterSet


class Query(ObjectType):
    config_compliance = ObjectField(ConfigComplianceType)
    config_compliance_list = ObjectListField(ConfigComplianceType)

    platform_setting = ObjectField(PlatformSettingType)
    platform_setting_list = ObjectListField(PlatformSettingType)

    configuration_request = ObjectField(ConfigurationRequestType)
    configuration_request_list = ObjectListField(ConfigurationRequestType)

    substitute = ObjectField(SubstituteType)
    substitute_list = ObjectListField(SubstituteType)


schema = Query
