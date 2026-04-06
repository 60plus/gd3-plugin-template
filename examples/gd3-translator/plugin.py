"""GD3 Translator plugin - translates game descriptions between languages.

Uses translate-shell (Python package) with Google Translate backend.
Long texts are split into chunks of ~450 characters at paragraph boundaries,
translated individually, and joined back together.

Config (Settings > Plugins > Translator):
  from_lang: source language (default: en)
  to_lang:   target language (default: pl)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from plugins.hookspecs import hookimpl

logger = logging.getLogger("plugin.gd3-translator")

CHUNK_SIZE = 450


def _get_config() -> dict:
    """Read plugin config from DB-stored JSON, fallback to plugin.json defaults."""
    try:
        # Try reading from installed plugin config (written by plugin manager)
        from config import PLUGINS_PATH
        cfg_path = Path(PLUGINS_PATH) / "gd3-translator" / "plugin.json"
        if cfg_path.exists():
            with open(cfg_path) as f:
                manifest = json.load(f)
                schema = manifest.get("config_schema", {})
                return {k: v.get("default") for k, v in schema.items()}
    except Exception:
        pass
    return {"from_lang": "en", "to_lang": "pl"}


def _translate_sync(text: str, from_lang: str, to_lang: str) -> str | None:
    """Run translate-shell in a separate thread to avoid asyncio.run() conflict.

    translate-shell internally calls asyncio.run() which fails inside FastAPI's
    already-running event loop. Running in a thread with its own loop fixes this.
    """
    import concurrent.futures

    def _worker():
        from translate_shell.translate import translate
        r = translate(text, target_lang=to_lang, source_lang=from_lang)
        if r.results and r.results[0].paraphrase:
            return r.results[0].paraphrase
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_worker)
        return future.result(timeout=60)


def translate_text(text: str, from_lang: str = "en", to_lang: str = "pl") -> dict:
    """Translate text, chunking if needed.

    Returns: {ok: bool, text: str, from_lang: str, to_lang: str, error: str}
    """
    if not text or not text.strip():
        return {"ok": False, "text": "", "error": "No text provided",
                "from_lang": from_lang, "to_lang": to_lang}

    text = text.strip()

    try:
        from translate_shell.translate import translate  # noqa: F401 - check import
    except ImportError:
        return {"ok": False, "text": "", "error": "translate-shell not installed",
                "from_lang": from_lang, "to_lang": to_lang}

    try:
        if len(text) <= CHUNK_SIZE:
            translated = _translate_sync(text, from_lang, to_lang)
            if translated:
                return {"ok": True, "text": translated,
                        "from_lang": from_lang, "to_lang": to_lang, "error": ""}
            return {"ok": False, "text": "", "error": "Translation returned empty result",
                    "from_lang": from_lang, "to_lang": to_lang}

        # Long text - split into chunks at paragraph boundaries
        paras = text.split("\n")
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for p in paras:
            if current and current_len + len(p) + 1 > CHUNK_SIZE:
                chunks.append("\n".join(current))
                current = [p]
                current_len = len(p)
            else:
                current.append(p)
                current_len += len(p) + 1
        if current:
            chunks.append("\n".join(current))

        translated_parts: list[str] = []
        for chunk in chunks:
            result = _translate_sync(chunk, from_lang, to_lang)
            if result:
                translated_parts.append(result)
            else:
                logger.warning("Translation chunk failed for %d chars", len(chunk))
                break

        if translated_parts:
            return {"ok": True, "text": "\n".join(translated_parts),
                    "from_lang": from_lang, "to_lang": to_lang, "error": ""}

        return {"ok": False, "text": "", "error": "All chunks failed",
                "from_lang": from_lang, "to_lang": to_lang}

    except Exception as e:
        logger.exception("Translation error")
        return {"ok": False, "text": "", "error": str(e)[:200],
                "from_lang": from_lang, "to_lang": to_lang}


class Plugin:
    """Translator plugin - lifecycle type (no metadata hooks needed).

    Provides translation via the /api/plugins/translate endpoint
    (registered by plugins_router when this plugin is loaded).
    The Plugin class itself only implements lifecycle hooks for logging.
    Translation logic is in translate_text() - called directly by the API.
    """

    @hookimpl
    def lifecycle_on_startup(self) -> None:
        logger.info("Translator plugin loaded (translate-shell backend)")
