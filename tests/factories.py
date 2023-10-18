import factory
import factory.fuzzy
from core.models import DataSource
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Platform, Site
from extras.models import ConfigTemplate
from factory.django import DjangoModelFactory
from ipam.models import IPAddress

from netbox_config_diff.models import ConfigCompliance, PlatformSetting


class ManufacturerFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"manufacturer-{n}")
    slug = factory.Sequence(lambda n: f"manufacturer-{n}")

    class Meta:
        model = Manufacturer


class DeviceTypeFactory(DjangoModelFactory):
    model = factory.Sequence(lambda n: f"model-{n}")
    slug = factory.Sequence(lambda n: f"model-{n}")
    manufacturer = factory.SubFactory(ManufacturerFactory)

    class Meta:
        model = DeviceType


class DeviceRoleFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"devicerole-{n}")
    slug = factory.Sequence(lambda n: f"devicerole-{n}")

    class Meta:
        model = DeviceRole


class SiteFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"site-{n}")
    slug = factory.Sequence(lambda n: f"site-{n}")

    class Meta:
        model = Site


class PlatformFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"platform-{n}")
    slug = factory.Sequence(lambda n: f"platform-{n}")

    class Meta:
        model = Platform


class IPAddressFactory(DjangoModelFactory):
    address = factory.Sequence(lambda n: f"{n}.{n}.{n}.{n}/32")

    class Meta:
        model = IPAddress


class ConfigTemplateFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"configcontext-{n}")
    template_code = factory.fuzzy.FuzzyText()

    class Meta:
        model = ConfigTemplate


class DeviceFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"device-{n}")
    site = factory.SubFactory(SiteFactory)
    device_type = factory.SubFactory(DeviceTypeFactory)
    device_role = factory.SubFactory(DeviceRoleFactory)
    platform = factory.SubFactory(PlatformFactory)
    primary_ip4 = factory.SubFactory(IPAddressFactory)
    config_template = factory.SubFactory(ConfigTemplateFactory)

    class Meta:
        model = Device


class PlatformSettingFactory(DjangoModelFactory):
    platform = factory.SubFactory(PlatformFactory)
    driver = factory.fuzzy.FuzzyChoice(["juniper_junos", "cisco_iosxe"])
    command = "show run"

    class Meta:
        model = PlatformSetting


class ConfigComplianceFactory(DjangoModelFactory):
    device = factory.SubFactory(DeviceFactory)

    class Meta:
        model = ConfigCompliance


class DataSourceFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"datasource-{n}")
    source_url = factory.Sequence(lambda n: f"/tmp/{n}")
    status = factory.fuzzy.FuzzyChoice(["new", "completed"])

    class Meta:
        model = DataSource
