from django.urls import include, path
from utilities.urls import get_model_urls

from netbox_config_diff import views

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
    # Configuration Requests
    path("configuration-requests/", views.ConfigurationRequestListView.as_view(), name="configurationrequest_list"),
    path("configuration-requests/add/", views.ConfigurationRequestEditView.as_view(), name="configurationrequest_add"),
    path("configuration-requests/<int:pk>/", include(get_model_urls("netbox_config_diff", "configurationrequest"))),
    # Jobs
    path("jobs/", views.JobListView.as_view(), name="configurationrequest_job_list"),
    # Configuration Requests
    path("substitutes/", views.SubstituteListView.as_view(), name="substitute_list"),
    path("substitutes/add/", views.SubstituteEditView.as_view(), name="substitute_add"),
    path("substitutes/<int:pk>/", include(get_model_urls("netbox_config_diff", "substitute"))),
)
