from django.urls import include, path
from utilities.urls import get_model_urls

from . import views

urlpatterns = (
    path("platform-settings/", views.PlatformSettingListView.as_view(), name="platformsetting_list"),
    path("platform-settings/add/", views.PlatformSettingEditView.as_view(), name="platformsetting_add"),
    path("platform-settings/edit/", views.PlatformSettingBulkEditView.as_view(), name="platformsetting_bulk_edit"),
    path(
        "platform-settings/delete/", views.PlatformSettingBulkDeleteView.as_view(), name="platformsetting_bulk_delete"
    ),
    path("platform-settings/<int:pk>/", include(get_model_urls("netbox_config_diff", "platformsetting"))),
)
