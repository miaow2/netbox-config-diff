from graphene import ObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from . import filtersets, models


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


class Query(ObjectType):
    config_compliance = ObjectField(ConfigComplianceType)
    config_compliance_list = ObjectListField(ConfigComplianceType)

    platform_setting = ObjectField(PlatformSettingType)
    platform_setting_list = ObjectListField(PlatformSettingType)


schema = Query
