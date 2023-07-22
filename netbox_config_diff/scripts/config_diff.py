from extras.scripts import Script

from netbox_config_diff.compliance.base import ConfigDiffBase


class ConfigDiffScript(ConfigDiffBase, Script):
    class Meta:
        description = "Checks for configuration difference."
        job_timeout = 600

    def run(self, data: dict, commit: bool) -> None:
        devices = self.validate_data(data)
        devices = list(self.get_devices_with_rendered_configs(devices))
        self.get_actual_configs(devices)
        self.get_diff(devices)
        self.update_in_db(devices)
