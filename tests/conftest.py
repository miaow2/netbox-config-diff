from typing import Protocol, TypedDict
from unittest.mock import Mock

import pytest
from typing_extensions import Unpack

from netbox_config_diff.compliance.base import ConfigDiffBase
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
            "devices": None,
            "data_source": None,
        }
        if fields.get("status"):
            data["data_source"] = DataSourceFactory.create(status=fields["status"])
            fields.pop("status")
        return data | fields

    return factory


@pytest.fixture()
def script_data(script_data_factory: "ScriptDataFactory") -> "ScriptData":
    return script_data_factory()
