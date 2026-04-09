"""Theme plugin template.

Provides custom layouts, CSS, JavaScript, and theme definitions to GamesDownloader.
Theme plugins can include Vue SFC files (.vue) that are compiled on container startup.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from plugins.hookspecs import hookimpl


class Plugin:
    """Theme provider - implements FrontendProviderSpec hooks."""

    @hookimpl
    def frontend_get_theme(self) -> dict[str, Any] | None:
        """Return a theme definition dict.

        Required fields: id, name, description, layout, skins, defaultSkin, cssFile
        Optional: font, previewHtml, settings
        See docs/HOOKS.md for the full theme definition reference.
        """
        return {
            "id": "my-theme",
            "name": "My Theme",
            "description": "A custom theme for GamesDownloader",
            "layout": "my-theme",  # must match registerPluginLayout() in compiled Vue
            "skins": [
                {"id": "blue", "name": "Ocean Blue", "preview": "#2563eb"},
                {"id": "red", "name": "Crimson", "preview": "#dc2626"},
            ],
            "defaultSkin": "blue",
            "cssFile": "my-theme",
            # Optional: Google Fonts URL
            # "font": "https://fonts.googleapis.com/css2?family=MyFont&display=swap",
            # Optional: custom preview HTML for Settings > Appearance (sanitized: div+span+style only)
            # "previewHtml": "<div style='...'>...</div>",
            "settings": [
                # Per-theme settings shown in Settings > Appearance > Theme Settings
                # Values are applied as CSS custom properties on :root
                # {
                #     "key": "glassBlur",
                #     "label": "Glass Blur",
                #     "hint": "Backdrop blur strength",
                #     "type": "range",
                #     "default": 20,
                #     "min": 0, "max": 60, "step": 1,
                #     "unit": "px",
                #     "cssVar": "--my-glass-blur",
                # },
            ],
        }

    @hookimpl
    def frontend_get_css(self) -> str | None:
        """Return CSS string injected into the page <head>."""
        css_path = Path(__file__).parent / "my-theme.css"
        if css_path.exists():
            return css_path.read_text(encoding="utf-8")
        return None

    @hookimpl
    def frontend_get_js(self) -> str | None:
        """Return JavaScript string injected into the page <head>.

        Plugin JS has access to window.__GD__ for Vue runtime, stores, API.
        See docs/HOOKS.md for the full window.__GD__ API reference.
        """
        js_path = Path(__file__).parent / "my-theme.js"
        if js_path.exists():
            return js_path.read_text(encoding="utf-8")
        return None
