from typing import Any


class DeviceError(Exception):
    def __str__(self) -> str:
        return f"{self.message}, {self.kwargs['devices']}"

    def __init__(self, message: str, **kwargs: Any) -> None:
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)


class DeviceValidationError(DeviceError):
    pass


class DeviceConfigurationError(DeviceError):
    pass
