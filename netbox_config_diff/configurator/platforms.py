import re
from typing import Any, Pattern

from scrapli_cfg.exceptions import TemplateError
from scrapli_cfg.platform.core.arista_eos import AsyncScrapliCfgEOS
from scrapli_cfg.platform.core.cisco_iosxe import AsyncScrapliCfgIOSXE
from scrapli_cfg.platform.core.cisco_iosxr import AsyncScrapliCfgIOSXR
from scrapli_cfg.platform.core.cisco_nxos import AsyncScrapliCfgNXOS
from scrapli_cfg.platform.core.juniper_junos import AsyncScrapliCfgJunos
from scrapli_cfg.response import ScrapliCfgResponse


class CustomScrapliCfg:
    def _render_substituted_config(
        self, config_template: str, substitutes: list[tuple[str, Pattern[str]]], source_config: str
    ) -> str:
        """
        Render a substituted configuration file

        Renders a configuration based on a user template, substitutes, and a target config from the
        device.

        Args:
            config_template: config file to use as the base for substitutions -- should contain
                jinja2-like variables that will be replaced with data fetched from the source config
                by the substitutes patterns
            substitutes: tuple of name, pattern -- where name matches the jinja2-like variable in
                the config_template file, and pattern is a compiled regular expression pattern to be
                used to fetch that section from the source config
            source_config: current source config to use in substitution process

        Returns:
            None

        Raises:
            TemplateError: if no substitute sections are provided
            TemplateError: if a substitute pattern is not found in the config template

        """
        self.logger.debug("rendering substituted config")

        if not substitutes:
            msg = "no substitutes provided..."
            self.logger.critical(msg)
            raise TemplateError(msg)

        replace_sections = [(name, re.search(pattern=pattern, string=source_config)) for name, pattern in substitutes]

        rendered_config = config_template
        for name, replace_section in replace_sections:
            if not replace_section:
                msg = f"substitution pattern {name} was unable to find a match in the target configsource"
                self.logger.critical(msg)
                raise TemplateError(msg)

            replace_group = replace_section.group()
            rendered_config = rendered_config.replace(f"{{{{ {name} }}}}", replace_group)

        # remove any totally empty lines (from bad regex, or just device spitting out lines w/
        # nothing on it
        rendered_config = "\n".join(line for line in rendered_config.splitlines() if line)

        self.logger.debug("rendering substituted config complete")

        return rendered_config

    async def render_substituted_config(
        self,
        config_template: str,
        substitutes: list[tuple[str, Pattern[str]]],
        source: str = "running",
    ) -> tuple[ScrapliCfgResponse, str]:
        """
        Render a substituted configuration file

        Renders a configuration based on a user template, substitutes, and a target config from the
        device.

        Args:
            config_template: config file to use as the base for substitutions -- should contain
                jinja2-like variables that will be replaced with data fetched from the source config
                by the substitutes patterns
            substitutes: tuple of name, pattern -- where name matches the jinja2-like variable in
                the config_template file, and pattern is a compiled regular expression pattern to be
                used to fetch that section from the source config
            source: config source to use for the substitution efforts, typically running|startup

        Returns:
            str: actual and substituted/rendered config

        Raises:
            N/A

        """
        self.logger.info("fetching configuration and replacing with provided substitutes")

        source_config = await self.get_config(config_template=config_template, source=source)
        return source_config, self._render_substituted_config(
            config_template=config_template,
            substitutes=substitutes,
            source_config=source_config.result,
        )

    async def get_config(self, **kwargs) -> ScrapliCfgResponse:
        kwargs.pop("config_template", None)
        return await super().get_config(**kwargs)


class CustomAsyncScrapliCfgEOS(CustomScrapliCfg, AsyncScrapliCfgEOS):
    pass


class CustomAsyncScrapliCfgIOSXE(CustomScrapliCfg, AsyncScrapliCfgIOSXE):
    pass


class CustomAsyncScrapliCfgIOSXR(CustomScrapliCfg, AsyncScrapliCfgIOSXR):
    pass


class CustomAsyncScrapliCfgNXOS(CustomScrapliCfg, AsyncScrapliCfgNXOS):
    pass


class CustomAsyncScrapliCfgJunos(CustomScrapliCfg, AsyncScrapliCfgJunos):
    is_set_config = False

    async def get_config(self, config_template: str, source: str = "running") -> ScrapliCfgResponse:
        response = self._pre_get_config(source=source)

        command = "show configuration"
        if re.findall(r"^set\s+", config_template, flags=re.I | re.M):
            self.is_set_config = True
            command += " | display set"

        if self._in_configuration_session is True:
            config_result = await self.conn.send_config(config=f"run {command}")
        else:
            config_result = await self.conn.send_command(command=command)

        return self._post_get_config(
            response=response,
            source=source,
            scrapli_responses=[config_result],
            result=config_result.result,
        )

    async def load_config(self, config: str, replace: bool = False, **kwargs: Any) -> ScrapliCfgResponse:
        """
        Load configuration to a device

        Supported kwargs:
            set: bool indicating config is a "set" style config (ignored if replace is True)

        Args:
            config: string of the configuration to load
            replace: replace the configuration or not, if false configuration will be loaded as a
                merge operation
            kwargs: additional kwargs that the implementing classes may need for their platform,
                see above for junos supported kwargs

        Returns:
            ScrapliCfgResponse: response object

        Raises:
            N/A

        """
        response = self._pre_load_config(config=config)

        config = self._prepare_load_config(config=config, replace=replace)

        config_result = await self.conn.send_config(config=config, privilege_level="root_shell")

        if self.is_set_config is True:
            load_config = f"load set {self.filesystem}{self.candidate_config_filename}"
        else:
            if self._replace is True:
                load_config = f"load override {self.filesystem}{self.candidate_config_filename}"
            else:
                load_config = f"load merge {self.filesystem}{self.candidate_config_filename}"

        load_result = await self.conn.send_config(config=load_config)
        self._in_configuration_session = True

        return self._post_load_config(
            response=response,
            scrapli_responses=[config_result, load_result],
        )
