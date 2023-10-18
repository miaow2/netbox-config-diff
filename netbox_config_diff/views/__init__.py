from .compliance import (
    ConfigComplianceBulkDeleteView,
    ConfigComplianceListView,
    PlatformSettingBulkDeleteView,
    PlatformSettingBulkEditView,
    PlatformSettingEditView,
    PlatformSettingListView,
)
from .configuration import (
    ConfigurationRequestEditView,
    ConfigurationRequestListView,
    JobListView,
    SubstituteEditView,
    SubstituteListView,
)

__all__ = (
    "ConfigComplianceBulkDeleteView",
    "ConfigComplianceListView",
    "ConfigurationRequestEditView",
    "ConfigurationRequestListView",
    "JobListView",
    "PlatformSettingBulkDeleteView",
    "PlatformSettingBulkEditView",
    "PlatformSettingEditView",
    "PlatformSettingListView",
    "SubstituteEditView",
    "SubstituteListView",
)
