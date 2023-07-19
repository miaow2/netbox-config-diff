from django.urls import include, path
from utilities.urls import get_model_urls

from . import views

urlpatterns = (
    # Config Compliances
    path("config-compliances/", views.ConfigComplianceListView.as_view(), name="configcompliance_list"),
    path(
        "config-compliances/delete/",
        views.ConfigComplianceBulkDeleteView.as_view(),
        name="configcompliance_bulk_delete",
    ),
    path("config-compliances/<int:pk>/", include(get_model_urls("netbox_config_diff", "configcompliance"))),
    # Platform Settings
    path("platform-settings/", views.PlatformSettingListView.as_view(), name="platformsetting_list"),
    path("platform-settings/add/", views.PlatformSettingEditView.as_view(), name="platformsetting_add"),
    path("platform-settings/edit/", views.PlatformSettingBulkEditView.as_view(), name="platformsetting_bulk_edit"),
    path(
        "platform-settings/delete/", views.PlatformSettingBulkDeleteView.as_view(), name="platformsetting_bulk_delete"
    ),
    path("platform-settings/<int:pk>/", include(get_model_urls("netbox_config_diff", "platformsetting"))),
)
