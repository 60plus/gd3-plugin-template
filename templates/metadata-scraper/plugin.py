"""Metadata scraper plugin template.

Replace the placeholder code with your actual scraping logic.
See examples/ppe-metadata/ for a complete working implementation.
"""

from __future__ import annotations

import logging
from typing import Any

from plugins.hookspecs import hookimpl

logger = logging.getLogger("plugin.my-metadata-scraper")


class Plugin:
    """Metadata provider - implements MetadataProviderSpec hooks."""

    @hookimpl
    def metadata_provider_name(self) -> str:
        return "My Source"

    @hookimpl
    def metadata_provider_id(self) -> str:
        return "mysource"

    @hookimpl
    def metadata_search_game(self, query: str) -> list[dict[str, Any]]:
        """Search for games by title.

        Must return a list of dicts with these keys:
          - provider_id: str (same as metadata_provider_id)
          - provider_game_id: str (unique ID or URL for this game)
          - name: str (game title)
          - snippet: str (short description, optional)
        """
        # TODO: implement your search logic here
        # Example:
        # results = my_api_search(query)
        # return [{"provider_id": "mysource", "provider_game_id": r["id"],
        #          "name": r["title"], "snippet": r.get("desc", "")}
        #         for r in results]
        return []

    @hookimpl
    def metadata_get_game(self, provider_game_id: str) -> dict[str, Any] | None:
        """Fetch full metadata for a game.

        Must return a dict with these keys (all optional except provider_id):
          - provider_id: str
          - provider_game_id: str
          - title: str
          - description: str (full text description)
          - rating: float (numeric score)
          - genre: str
          - release_date: str (YYYY-MM-DD format)
          - developer: str
          - screenshots: list[str] (image URLs)
          - source_url: str (link to the source page)
        """
        # TODO: implement your fetch logic here
        return None

    @hookimpl
    def metadata_get_cover_url(self, provider_game_id: str) -> str | None:
        """Return a cover image URL for the game."""
        # TODO: implement
        return None
