from typing import TYPE_CHECKING

import pytest
from dcim.models import Device
from utilities.exceptions import AbortScript

from netbox_config_diff.models import ConfigCompliance
from tests.factories import ConfigComplianceFactory, DeviceFactory, PlatformSettingFactory

if TYPE_CHECKING:
    from netbox_config_diff.compliance.base import ConfigDiffBase
    from tests.conftest import ScriptData, ScriptDataFactory


def test_validate_data_no_data(mock_config_diff: "ConfigDiffBase", script_data: "ScriptData") -> None:
    with pytest.raises(AbortScript) as e:
        mock_config_diff.validate_data(data=script_data)
    assert str(e.value) == "Define site or devices"


@pytest.mark.django_db()
def test_validate_data_no_sync_datasource(
    mock_config_diff: "ConfigDiffBase", script_data_factory: "ScriptDataFactory"
) -> None:
    with pytest.raises(AbortScript) as e:
        mock_config_diff.validate_data(data=script_data_factory(**{"site": "test", "devices": "test", "status": "new"}))
    assert str(e.value) == "Define synced DataSource"


@pytest.mark.django_db()
def test_validate_data_no_platformsetting(
    mock_config_diff: "ConfigDiffBase", script_data_factory: "ScriptDataFactory"
) -> None:
    DeviceFactory.create()
    DeviceFactory.create()
    devices = mock_config_diff.validate_data(data=script_data_factory(**{"devices": Device.objects.all()}))

    assert len(devices) == 0


@pytest.mark.django_db()
def test_validate_data(mock_config_diff: "ConfigDiffBase", script_data_factory: "ScriptDataFactory") -> None:
    device = DeviceFactory.create()
    DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform)
    devices = mock_config_diff.validate_data(data=script_data_factory(**{"devices": Device.objects.all()}))

    assert len(devices) == 1


@pytest.mark.django_db()
def test_device_data(mock_config_diff: "ConfigDiffBase", script_data_factory: "ScriptDataFactory") -> None:
    device = DeviceFactory.create()
    DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform)
    devices = mock_config_diff.validate_data(data=script_data_factory(**{"devices": Device.objects.all()}))
    devices = list(mock_config_diff.get_devices_with_rendered_configs(devices))

    assert len(devices) == 1
    assert Device.objects.first().pk == devices[0].pk
    assert Device.objects.first().name == devices[0].name
    assert Device.objects.first().platform.platform_setting.driver == devices[0].platform
    assert Device.objects.first().platform.platform_setting.command == devices[0].command
    assert Device.objects.first().platform.platform_setting.exclude_regex == devices[0].exclude_regex


@pytest.mark.django_db()
def test_configcompliance_update() -> None:
    ConfigComplianceFactory.create()
    obj = ConfigCompliance.objects.first()
    kwargs = {
        "status": "compliant",
        "diff": "no diff",
        "rendered_config": "rendered_config",
        "actual_config": "actual_config",
    }
    obj.update(commit=True, **kwargs)
    assert obj.status == "compliant"
    assert obj.diff == "no diff"
    assert obj.rendered_config == "rendered_config"
    assert obj.actual_config == "actual_config"
