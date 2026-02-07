from django.urls import include, path
from utilities.urls import get_model_urls

from netbox_config_diff import views

urlpatterns = (
    # Config Compliances
    path("config-compliances/", include(get_model_urls("netbox_config_diff", "configcompliance", detail=False))),
    path("config-compliances/<int:pk>/", include(get_model_urls("netbox_config_diff", "configcompliance"))),
    # Platform Settings
    path("platform-settings/", include(get_model_urls("netbox_config_diff", "platformsetting", detail=False))),
    path("platform-settings/<int:pk>/", include(get_model_urls("netbox_config_diff", "platformsetting"))),
    # Configuration Requests
    path(
        "configuration-requests/", include(get_model_urls("netbox_config_diff", "configurationrequest", detail=False))
    ),
    path("configuration-requests/<int:pk>/", include(get_model_urls("netbox_config_diff", "configurationrequest"))),
    # Jobs
    path("jobs/", views.JobListView.as_view(), name="configurationrequest_job_list"),
    # Configuration Requests
    path("substitutes/", include(get_model_urls("netbox_config_diff", "substitute", detail=False))),
    path("substitutes/<int:pk>/", include(get_model_urls("netbox_config_diff", "substitute"))),
)
