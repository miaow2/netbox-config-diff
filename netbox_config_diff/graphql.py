from graphene import ObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from . import filtersets, models


class PlatformSettingType(NetBoxObjectType):
    class Meta:
        model = models.PlatformSetting
        fields = "__all__"
        filterset_class = filtersets.PlatformSetting


class Query(ObjectType):
    platform_setting = ObjectField(PlatformSettingType)
    platform_setting_list = ObjectListField(PlatformSettingType)


schema = Query
