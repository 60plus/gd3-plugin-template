"""NEON HORIZON — futuristic theme plugin for GamesDownloader.

Provides a modern theme with animated gradient backgrounds, floating particles,
glass morphism, neon glow effects, and Orbitron typography.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from plugins.hookspecs import hookimpl


class Plugin:
    """NEON HORIZON theme plugin."""

    @hookimpl
    def frontend_get_theme(self) -> dict[str, Any] | None:
        """Return the NEON HORIZON theme definition."""
        return {
            "id": "neon-horizon",
            "name": "NEON HORIZON",
            "description": "Futuristic theme with animated gradients, particles, and neon glow",
            "layout": "neon-horizon",
            "skins": [
                {"id": "nh-cyan",    "name": "Cyan Flux",     "preview": "#00d4ff"},
                {"id": "nh-violet",  "name": "Violet Surge",  "preview": "#7b2fff"},
                {"id": "nh-magenta", "name": "Magenta Pulse", "preview": "#e040fb"},
                {"id": "nh-gold",    "name": "Gold Circuit",  "preview": "#fbbf24"},
                {"id": "nh-cyber",   "name": "Cyber",  "preview": "linear-gradient(135deg,#00d4ff,#7b2fff)", "dual": True},
                {"id": "nh-plasma",  "name": "Plasma", "preview": "linear-gradient(135deg,#e040fb,#00d4ff)", "dual": True},
                {"id": "nh-sunset",  "name": "Sunset", "preview": "linear-gradient(135deg,#f97316,#e040fb)", "dual": True},
                {"id": "nh-aurora",  "name": "Aurora", "preview": "linear-gradient(135deg,#22c55e,#00d4ff)", "dual": True},
            ],
            "defaultSkin": "nh-cyber",
            "cssFile": "neon-horizon",
            "font": "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap",
            "settings": [
                {"key": "particleCount", "label": "Particle Count", "hint": "Floating background particles",
                 "type": "select", "default": "6", "options": ["0","3","6","12"],
                 "optionLabels": ["None","Few","Normal","Many"], "cssVar": "--nh-particle-count"},
                {"key": "glowIntensity", "label": "Neon Glow", "hint": "Glow intensity on cards and text",
                 "type": "range", "default": 1, "min": 0, "max": 2, "step": 0.1, "cssVar": "--nh-glow-mult"},
                {"key": "glassBlur", "label": "Glass Blur", "hint": "Backdrop blur for glass panels",
                 "type": "range", "default": 20, "min": 0, "max": 60, "step": 1, "unit": "px", "cssVar": "--glass-blur-px"},
                {"key": "scanlines", "label": "Scanline Overlay", "hint": "CRT-style horizontal lines",
                 "type": "toggle", "default": False, "cssVar": "--nh-scanlines"},
                {"key": "bgSpeed", "label": "BG Animation Speed", "hint": "Gradient shift animation",
                 "type": "select", "default": "20s", "options": ["10s","20s","40s","0s"],
                 "optionLabels": ["Fast","Normal","Slow","Off"], "cssVar": "--nh-bg-speed"},
            ],
        }

    @hookimpl
    def frontend_get_css(self) -> str | None:
        css_path = Path(__file__).parent / "neon-horizon.css"
        return css_path.read_text(encoding="utf-8") if css_path.exists() else None

    @hookimpl
    def frontend_get_js(self) -> str | None:
        js_path = Path(__file__).parent / "neon-horizon.js"
        return js_path.read_text(encoding="utf-8") if js_path.exists() else None
