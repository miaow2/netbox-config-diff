from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from netbox_config_diff.models import ConfigCompliance, PlatformSetting
from tests.factories import ConfigComplianceFactory, PlatformSettingFactory


@pytest.mark.django_db()
def test_configcompliance_list(admin_client: Client) -> None:
    response = admin_client.get(reverse("plugins:netbox_config_diff:configcompliance_list"))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_configcompliance(admin_client: Client) -> None:
    config = ConfigComplianceFactory.create()
    response = admin_client.get(reverse("plugins:netbox_config_diff:configcompliance", args=[config.pk]))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_configcompliance_delete(admin_client: Client) -> None:
    config = ConfigComplianceFactory.create()
    admin_client.post(
        reverse("plugins:netbox_config_diff:configcompliance_delete", kwargs={"pk": config.pk}), data={"confirm": True}
    )

    assert ConfigCompliance.objects.all().count() == 0


@pytest.mark.django_db()
def test_configcompliance_add(admin_client: Client) -> None:
    with pytest.raises(NoReverseMatch):
        admin_client.get(reverse("plugins:netbox_config_diff:configcompliance_add"))


@pytest.mark.django_db()
def test_platformsetting_list(admin_client: Client) -> None:
    response = admin_client.get(reverse("plugins:netbox_config_diff:platformsetting_list"))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_platformsetting_add(admin_client: Client) -> None:
    response = admin_client.get(reverse("plugins:netbox_config_diff:platformsetting_add"))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_platformsetting(admin_client: Client) -> None:
    platform = PlatformSettingFactory.create()
    response = admin_client.get(reverse("plugins:netbox_config_diff:platformsetting", args=[platform.pk]))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_platformsetting_delete(admin_client: Client) -> None:
    platform = PlatformSettingFactory.create()
    admin_client.post(
        reverse("plugins:netbox_config_diff:platformsetting_delete", kwargs={"pk": platform.pk}), data={"confirm": True}
    )

    assert PlatformSetting.objects.all().count() == 0
