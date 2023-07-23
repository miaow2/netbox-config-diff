from extras.scripts import Script

from netbox_config_diff.compliance.base import ConfigDiffBase


class ConfigDiffScript(ConfigDiffBase, Script):
    class Meta:
        description = "Checks for configuration difference."
        job_timeout = 600

    def run(self, data: dict, commit: bool) -> None:
        self.run_script(data)
