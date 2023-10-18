import re
from typing import Pattern

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

        rendered_config = ""
        for name, replace_section in replace_sections:
            if not replace_section:
                msg = f"substitution pattern {name} was unable to find a match in the target config" " source"
                self.logger.critical(msg)
                raise TemplateError(msg)

            replace_group = replace_section.group()
            rendered_config = config_template.replace(f"{{{{ {name} }}}}", replace_group)

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

        source_config = await self.get_config(source=source)
        return source_config, self._render_substituted_config(
            config_template=config_template,
            substitutes=substitutes,
            source_config=source_config.result,
        )


class CustomAsyncScrapliCfgEOS(CustomScrapliCfg, AsyncScrapliCfgEOS):
    pass


class CustomAsyncScrapliCfgIOSXE(CustomScrapliCfg, AsyncScrapliCfgIOSXE):
    pass


class CustomAsyncScrapliCfgIOSXR(CustomScrapliCfg, AsyncScrapliCfgIOSXR):
    pass


class CustomAsyncScrapliCfgNXOS(CustomScrapliCfg, AsyncScrapliCfgNXOS):
    pass


class CustomAsyncScrapliCfgJunos(CustomScrapliCfg, AsyncScrapliCfgJunos):
    pass
