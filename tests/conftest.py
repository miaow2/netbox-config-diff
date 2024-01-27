from typing import Protocol, TypedDict
from unittest.mock import Mock

import pytest
from faker import Faker
from typing_extensions import Unpack

from netbox_config_diff.compliance.base import ConfigDiffBase
from netbox_config_diff.models import ConplianceDeviceDataClass
from tests.factories import DataSourceFactory


class ScriptData(TypedDict, total=False):
    site: str | None
    devices: list[str] | None
    data_source: str | None


class ScriptDataFactory(Protocol):
    def __call__(self, **fields: Unpack[ScriptData]) -> "ScriptData":
        """Script data factory protocol."""


@pytest.fixture()
def mock_config_diff() -> ConfigDiffBase:
    mock_object = ConfigDiffBase
    mock_object.log_warning = Mock()
    mock_object.log_info = Mock()
    return mock_object()


@pytest.fixture()
def script_data_factory() -> "ScriptDataFactory":
    def factory(**fields: Unpack["ScriptData"]) -> "ScriptData":
        data = {
            "site": None,
            "role": None,
            "devices": None,
            "data_source": None,
            "status": "active",
        }
        if fields.get("data_source_status"):
            data["data_source"] = DataSourceFactory.create(status=fields["data_source_status"])
            fields.pop("data_source_status")
        return data | fields

    return factory


@pytest.fixture()
def script_data(script_data_factory: "ScriptDataFactory") -> "ScriptData":
    return script_data_factory()


class DeviceDataClassData(TypedDict, total=False):
    pk: int
    name: str
    mgmt_ip: str
    platform: str
    command: str
    username: str
    password: str
    auth_strict_key: bool
    transport: bool
    diff: str | None
    exclude_regex: str | None
    rendered_config: str | None
    actual_config: str | None
    error: str | None
    missing: str | None
    extra: str | None


class DeviceDataClassDataFactory(Protocol):
    def __call__(self, **fields: Unpack[DeviceDataClassData]) -> "DeviceDataClassData":
        """DeviceDataClass data factory protocol."""


@pytest.fixture()
def devicedataclass_factory() -> "DeviceDataClassDataFactory":
    def factory(**fields: Unpack["DeviceDataClassData"]) -> "DeviceDataClassData":
        faker = Faker()
        data = {
            "pk": faker.random_digit(),
            "name": faker.hostname(),
            "mgmt_ip": faker.ipv4(),
            "platform": faker.random_choices(["juniper_junos", "cisco_iosxe"]),
            "command": "sh run",
            "username": faker.name(),
            "password": faker.password(),
            "auth_strict_key": False,
            "transport": "asyncssh",
            "device": None,
        }
        return data | fields

    return factory


@pytest.fixture()
def devicedataclass_data(devicedataclass_factory: "DeviceDataClassDataFactory") -> ConplianceDeviceDataClass:
    data = devicedataclass_factory()
    return ConplianceDeviceDataClass(**data)
