from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from users.models import User

from netbox_config_diff.choices import ConfigurationRequestStatusChoices
from tests.factories import (
    ConfigurationRequestFactory,
    DeviceFactory,
    PlatformSettingFactory,
)

if TYPE_CHECKING:
    pass


@pytest.mark.django_db()
def test_configuration_request_list(authenticated_api_client):
    device = DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform)
    ConfigurationRequestFactory.create(devices=[device])
    ConfigurationRequestFactory.create(devices=[device])

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    response = authenticated_api_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["count"] == 2
    assert len(response.json()["results"]) == 2


@pytest.mark.django_db()
def test_configuration_request_retrieve(authenticated_api_client):
    device = DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform)
    cr = ConfigurationRequestFactory.create(devices=[device])

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-detail", args=[cr.pk])
    response = authenticated_api_client.get(url)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == cr.pk
    assert data["status"]["value"] == ConfigurationRequestStatusChoices.CREATED
    assert len(data["devices"]) == 1
    assert data["devices"][0]["id"] == device.pk


@pytest.mark.django_db()
def test_configuration_request_create_success(authenticated_api_client, admin_user):
    device = DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform)

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {
        "devices": [device.pk],
        "description": "Test configuration request",
        "comments": "Test comments",
    }
    response = authenticated_api_client.post(url, payload, format="json")

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["status"]["value"] == ConfigurationRequestStatusChoices.CREATED
    assert data["description"] == "Test configuration request"
    assert data["comments"] == "Test comments"
    assert len(data["devices"]) == 1
    assert data["created_by"]["id"] == admin_user.pk


@pytest.mark.django_db()
def test_configuration_request_create_multiple_devices(authenticated_api_client):
    device1 = DeviceFactory.create()
    device2 = DeviceFactory.create()
    PlatformSettingFactory.create(platform=device1.platform)
    PlatformSettingFactory.create(platform=device2.platform)

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {
        "devices": [device1.pk, device2.pk],
        "description": "Multi-device request",
    }
    response = authenticated_api_client.post(url, payload, format="json")

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert len(data["devices"]) == 2
    device_ids = {d["id"] for d in data["devices"]}
    assert device1.pk in device_ids
    assert device2.pk in device_ids


@pytest.mark.django_db()
def test_configuration_request_create_no_platform_setting(authenticated_api_client):
    device = DeviceFactory.create()

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {
        "devices": [device.pk],
    }
    response = authenticated_api_client.post(url, payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "devices" in data
    assert "Assign PlatformSetting" in str(data["devices"])


@pytest.mark.django_db()
def test_configuration_request_create_unsupported_driver(authenticated_api_client):
    device = DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform, driver="unsupported_driver")

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {
        "devices": [device.pk],
    }
    response = authenticated_api_client.post(url, payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "devices" in data
    assert "Driver(s) not supported" in str(data["devices"])


@pytest.mark.django_db()
def test_configuration_request_create_no_config_template(authenticated_api_client):
    device = DeviceFactory.create(config_template=None)
    PlatformSettingFactory.create(platform=device.platform)

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {
        "devices": [device.pk],
    }
    response = authenticated_api_client.post(url, payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "devices" in data
    assert "Define config template" in str(data["devices"])


@pytest.mark.django_db()
def test_configuration_request_create_mixed_valid_invalid_devices(authenticated_api_client):
    valid_device = DeviceFactory.create()
    PlatformSettingFactory.create(platform=valid_device.platform)
    invalid_device = DeviceFactory.create()

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {
        "devices": [valid_device.pk, invalid_device.pk],
    }
    response = authenticated_api_client.post(url, payload, format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "devices" in data


@pytest.mark.django_db()
def test_configuration_request_create_empty_devices(authenticated_api_client):
    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {
        "devices": [],
    }
    response = authenticated_api_client.post(url, payload, format="json")

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert len(data["devices"]) == 0


@pytest.mark.django_db()
def test_configuration_request_create_without_authentication(api_client):
    device = DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform)

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {
        "devices": [device.pk],
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db()
def test_configuration_request_list_filtering(authenticated_api_client):
    device = DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform)

    cr = ConfigurationRequestFactory.create(devices=[device], status=ConfigurationRequestStatusChoices.CREATED)
    ConfigurationRequestFactory.create(devices=[device], status=ConfigurationRequestStatusChoices.APPROVED)

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")

    response = authenticated_api_client.get(url, {"status": ConfigurationRequestStatusChoices.CREATED})

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert any(r["id"] == cr.pk for r in data["results"])


@pytest.mark.django_db()
def test_configuration_request_retrieve_nonexistent(authenticated_api_client):
    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-detail", args=[9999])
    response = authenticated_api_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db()
def test_configuration_request_create_sets_created_by(authenticated_api_client, admin_user):
    user2 = User.objects.create_user(username="user2", password="pass")

    device = DeviceFactory.create()
    PlatformSettingFactory.create(platform=device.platform)

    url = reverse("plugins-api:netbox_config_diff-api:configurationrequest-list")
    payload = {"devices": [device.pk]}
    response = authenticated_api_client.post(url, payload, format="json")

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()

    assert data["created_by"]["id"] == admin_user.pk
    assert data["created_by"]["id"] != user2.pk
