from typing import TYPE_CHECKING, Any, Callable

from scrapli.driver.core import (
    AsyncEOSDriver,
    AsyncIOSXEDriver,
    AsyncIOSXRDriver,
    AsyncJunosDriver,
    AsyncNXOSDriver,
)
from scrapli.driver.network import AsyncNetworkDriver, NetworkDriver
from scrapli_cfg.exceptions import ScrapliCfgException
from scrapli_cfg.logging import logger

from .platforms import (
    CustomAsyncScrapliCfgEOS,
    CustomAsyncScrapliCfgIOSXE,
    CustomAsyncScrapliCfgIOSXR,
    CustomAsyncScrapliCfgJunos,
    CustomAsyncScrapliCfgNXOS,
)

ASYNC_CORE_PLATFORM_MAP = {
    AsyncEOSDriver: CustomAsyncScrapliCfgEOS,
    AsyncIOSXEDriver: CustomAsyncScrapliCfgIOSXE,
    AsyncIOSXRDriver: CustomAsyncScrapliCfgIOSXR,
    AsyncNXOSDriver: CustomAsyncScrapliCfgNXOS,
    AsyncJunosDriver: CustomAsyncScrapliCfgJunos,
}

if TYPE_CHECKING:
    from scrapli_cfg.platform.base.async_platform import AsyncScrapliCfgPlatform


def AsyncScrapliCfg(
    conn: AsyncNetworkDriver,
    *,
    config_sources: list[str] | None = None,
    on_prepare: Callable[..., Any] | None = None,
    dedicated_connection: bool = False,
    ignore_version: bool = False,
    **kwargs: Any,
) -> "AsyncScrapliCfgPlatform":
    """
    Scrapli Config Async Factory

    Return a async scrapli config object for the provided platform. Prefer to use factory classes
    just so that the naming convention (w/ upper case things) is "right", but given that the class
    version inherited from the base ScrapliCfgPlatform and did not implement the abstract methods
    this felt like a better move.

    Args:
        conn: scrapli connection to use
        config_sources: list of config sources
        on_prepare: optional callable to run at connection `prepare`
        dedicated_connection: if `False` (default value) scrapli cfg will not open or close the
            underlying scrapli connection and will raise an exception if the scrapli connection
            is not open. If `True` will automatically open and close the scrapli connection when
            using with a context manager, `prepare` will open the scrapli connection (if not
            already open), and `close` will close the scrapli connection.
        ignore_version: ignore checking device version support; currently this just means that
            scrapli-cfg will not fetch the device version during the prepare phase, however this
            will (hopefully) be used in the future to limit what methods can be used against a
            target device. For example, for EOS devices we need > 4.14 to load configs; so if a
            device is encountered at 4.13 the version check would raise an exception rather than
            just failing in a potentially awkward fashion.
        kwargs: keyword args to pass to the scrapli_cfg object (for things like iosxe 'filesystem'
            argument)

    Returns:
        AsyncScrapliCfg: async scrapli cfg object

    Raises:
        ScrapliCfgException: if provided connection object is sync
        ScrapliCfgException: if provided connection object is async but is not a supported ("core")
            platform type

    """
    logger.debug("AsyncScrapliCfg factory initialized")

    if isinstance(conn, NetworkDriver):
        raise ScrapliCfgException(
            "provided scrapli connection is sync but using 'AsyncScrapliCfg' -- you must use an "
            "async connection with 'AsyncScrapliCfg'!"
        )

    platform_class = ASYNC_CORE_PLATFORM_MAP.get(type(conn))
    if not platform_class:
        raise ScrapliCfgException(f"scrapli connection object type '{type(conn)}' not a supported scrapli-cfg type")

    final_platform: "AsyncScrapliCfgPlatform" = platform_class(
        conn=conn,
        config_sources=config_sources,
        on_prepare=on_prepare,
        dedicated_connection=dedicated_connection,
        ignore_version=ignore_version,
        **kwargs,
    )

    return final_platform
