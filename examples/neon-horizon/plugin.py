"""NEON HORIZON - futuristic theme plugin for GamesDownloader.

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
            "previewHtml": (
                '<div style="display:flex;flex-direction:column;height:100%;background:#05050f;overflow:hidden">'
                '  <div style="height:11px;display:flex;align-items:center;gap:2px;padding:0 4px;'
                '    background:rgba(0,212,255,.04);border-bottom:1px solid rgba(0,212,255,.15)">'
                '    <div style="width:7px;height:7px;border-radius:2px;background:#00d4ff;opacity:.7"></div>'
                '    <div style="width:12px;height:3px;border-radius:1px;background:#00d4ff;opacity:.8"></div>'
                '    <div style="width:12px;height:3px;border-radius:1px;background:rgba(255,255,255,.12)"></div>'
                '    <div style="width:12px;height:3px;border-radius:1px;background:rgba(255,255,255,.12)"></div>'
                '  </div>'
                '  <div style="height:34px;position:relative;'
                '    background:linear-gradient(135deg,rgba(0,212,255,.15),rgba(123,47,255,.2),rgba(5,5,15,.9))">'
                '    <div style="position:absolute;bottom:3px;left:5px;width:36px;height:4px;border-radius:1px;'
                '      background:linear-gradient(90deg,#00d4ff,#7b2fff);opacity:.8"></div>'
                '    <div style="position:absolute;bottom:8px;left:5px;font-size:5px;font-weight:900;'
                '      color:#fff;font-family:sans-serif;letter-spacing:.5px;'
                '      text-shadow:0 0 6px rgba(0,212,255,.6)">GAME TITLE</div>'
                '  </div>'
                '  <div style="display:flex;gap:2px;padding:3px 4px;flex:1;align-items:flex-start">'
                '    <div style="flex:1;aspect-ratio:16/9;border-radius:2px;'
                '      background:linear-gradient(180deg,rgba(0,212,255,.08),rgba(5,5,15,.7));'
                '      border:1px solid rgba(0,212,255,.1);border-bottom:1px solid #00d4ff"></div>'
                '    <div style="flex:1;aspect-ratio:16/9;border-radius:2px;'
                '      background:linear-gradient(180deg,rgba(123,47,255,.08),rgba(5,5,15,.7));'
                '      border:1px solid rgba(123,47,255,.1);border-bottom:1px solid #7b2fff"></div>'
                '    <div style="flex:1;aspect-ratio:16/9;border-radius:2px;'
                '      background:linear-gradient(180deg,rgba(0,212,255,.06),rgba(5,5,15,.7));'
                '      border:1px solid rgba(0,212,255,.08);border-bottom:1px solid #00d4ff"></div>'
                '  </div>'
                '  <div style="position:absolute;top:13px;right:5px;width:4px;height:4px;'
                '    border-radius:50%;background:rgba(0,212,255,.4)"></div>'
                '</div>'
            ),
            "skins": [
                # Solid skins
                {"id": "nh-cyan",    "name": "Cyan Flux",     "preview": "#00d4ff"},
                {"id": "nh-violet",  "name": "Violet Surge",  "preview": "#7b2fff"},
                {"id": "nh-magenta", "name": "Magenta Pulse", "preview": "#e040fb"},
                {"id": "nh-gold",    "name": "Gold Circuit",  "preview": "#fbbf24"},
                # Dual-color gradient skins
                {
                    "id": "nh-cyber", "name": "Cyber",
                    "preview": "linear-gradient(135deg,#00d4ff,#7b2fff)",
                    "dual": True,
                },
                {
                    "id": "nh-plasma", "name": "Plasma",
                    "preview": "linear-gradient(135deg,#e040fb,#00d4ff)",
                    "dual": True,
                },
                {
                    "id": "nh-sunset", "name": "Sunset",
                    "preview": "linear-gradient(135deg,#f97316,#e040fb)",
                    "dual": True,
                },
                {
                    "id": "nh-aurora", "name": "Aurora",
                    "preview": "linear-gradient(135deg,#22c55e,#00d4ff)",
                    "dual": True,
                },
            ],
            "defaultSkin": "nh-cyber",
            "cssFile": "neon-horizon",
            "font": (
                "https://fonts.googleapis.com/css2?"
                "family=Orbitron:wght@400;700;900&"
                "family=Rajdhani:wght@400;500;600;700&display=swap"
            ),
            "settings": [
                {
                    "key": "particleCount",
                    "label": "nh.setting_particles",
                    "hint": "nh.setting_particles_hint",
                    "type": "select",
                    "default": "6",
                    "options": ["0", "3", "6", "12"],
                    "optionLabels": ["nh.opt_none", "nh.opt_few", "nh.opt_normal", "nh.opt_many"],
                    "cssVar": "--nh-particle-count",
                },
                {
                    "key": "glassBlur",
                    "label": "nh.setting_glass_blur",
                    "hint": "nh.setting_glass_blur_hint",
                    "type": "range",
                    "default": 20,
                    "min": 0,
                    "max": 60,
                    "step": 1,
                    "unit": "px",
                    "cssVar": "--glass-blur-px",
                },
                {
                    "key": "glassOpacity",
                    "label": "nh.setting_glass_opacity",
                    "hint": "nh.setting_glass_opacity_hint",
                    "type": "range",
                    "default": 0.35,
                    "min": 0.05,
                    "max": 0.9,
                    "step": 0.05,
                    "cssVar": "--nh-glass-opacity",
                },
                {
                    "key": "scanlines",
                    "label": "nh.setting_scanlines",
                    "hint": "nh.setting_scanlines_hint",
                    "type": "toggle",
                    "default": False,
                    "cssVar": "--nh-scanlines",
                },
            ],
        }

    @hookimpl
    def frontend_get_css(self) -> str | None:
        """Return the NEON HORIZON CSS."""
        css_path = Path(__file__).parent / "neon-horizon.css"
        if css_path.exists():
            return css_path.read_text(encoding="utf-8")
        return None

    @hookimpl
    def frontend_get_js(self) -> str | None:
        """Return the NEON HORIZON JavaScript (particles, gradient overlay, etc.)."""
        js_path = Path(__file__).parent / "neon-horizon.js"
        if js_path.exists():
            return js_path.read_text(encoding="utf-8")
        return None
