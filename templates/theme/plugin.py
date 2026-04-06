"""Theme plugin template.

Provides custom CSS and/or theme definitions to GamesDownloader.
"""

from __future__ import annotations

from pathlib import Path

from plugins.hookspecs import hookimpl


class Plugin:
    """Theme provider - implements FrontendProviderSpec hooks."""

    @hookimpl
    def frontend_get_theme(self) -> dict | None:
        """Return a theme definition dict, or None.

        The dict can include:
          - id: str (unique theme ID)
          - name: str (display name)
          - layout: "modern" or "classic"
          - skins: list of skin dicts
          - cssFile: str (path to CSS file)
        """
        return None

    @hookimpl
    def frontend_get_css(self) -> str | None:
        """Return CSS string to inject into the page <head>.

        Read from a CSS file in the plugin directory:
        """
        css_path = Path(__file__).parent / "theme.css"
        if css_path.exists():
            return css_path.read_text(encoding="utf-8")
        return None
