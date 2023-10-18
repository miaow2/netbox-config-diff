from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_config_diff"

router = NetBoxRouter()
router.register("config-compliances", views.ConfigComplianceViewSet)
router.register("platform-settings", views.PlatformSettingViewSet)
router.register("configuration-requests", views.ConfigurationRequestViewSet)
router.register("substitutes", views.SubstituteViewSet)

urlpatterns = router.urls
