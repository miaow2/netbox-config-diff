from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_config_diff"

router = NetBoxRouter()
router.register("platform-settings", views.PlatformSettingViewSet)

urlpatterns = router.urls
