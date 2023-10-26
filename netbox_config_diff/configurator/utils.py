import logging

from django.utils import timezone
from extras.choices import LogLevelChoices


class CustomLogger:
    def __init__(self) -> None:
        self.log_data = []
        self.diffs = []
        self.logger = logging.getLogger("netbox_config_diff.configurator")

    def _log(self, message: str, log_level: str | None = None) -> None:
        if log_level not in LogLevelChoices.values():
            raise Exception(f"Unknown logging level: {log_level}")
        if log_level is None:
            log_level = LogLevelChoices.LOG_DEFAULT
        self.log_data.append((timezone.now().strftime("%Y-%m-%d %H:%M:%S"), log_level, message))

    def log(self, message: str) -> None:
        self._log(message, log_level=LogLevelChoices.LOG_DEFAULT)
        self.logger.info(message)

    def log_success(self, message: str) -> None:
        self._log(message, log_level=LogLevelChoices.LOG_SUCCESS)
        self.logger.info(message)

    def log_info(self, message: str) -> None:
        self._log(message, log_level=LogLevelChoices.LOG_INFO)
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        self._log(message, log_level=LogLevelChoices.LOG_WARNING)
        self.logger.info(message)

    def log_failure(self, message: str) -> None:
        self._log(message, log_level=LogLevelChoices.LOG_FAILURE)
        self.logger.info(message)

    def clear_log(self) -> None:
        self.log_data = []

    def logs(self) -> dict:
        return {"logs": self.log_data}

    def get_diffs(self) -> dict:
        return {"diffs": self.diffs}

    def get_data(self) -> dict:
        return self.get_diffs() | self.logs()

    def add_diff(self, name: str, diff: str | None = None, error: str | None = None) -> None:
        self.diffs.append({"name": name, "diff": diff, "error": error})
