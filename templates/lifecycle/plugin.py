"""Lifecycle plugin template.

Hook into app events: startup, shutdown, game added, download complete.
Can also register custom API endpoints.
See examples/gd3-translator/ for a complete working implementation.
"""

from __future__ import annotations

import logging

from plugins.hookspecs import hookimpl

logger = logging.getLogger("plugin.my-lifecycle")


class Plugin:
    """Lifecycle plugin - implements LifecycleSpec hooks."""

    @hookimpl
    def lifecycle_on_startup(self) -> None:
        """Called when the app starts.

        Use this to:
        - Register custom API endpoints on the FastAPI app
        - Start background tasks
        - Initialize resources

        Example - register a custom endpoint:

            from main import app

            @app.get("/api/plugins/my-endpoint")
            async def my_endpoint():
                return {"status": "ok"}
        """
        logger.info("My lifecycle plugin started")
        # TODO: add your startup logic here

    @hookimpl
    def lifecycle_on_shutdown(self) -> None:
        """Called when the app shuts down. Clean up resources."""
        # TODO: add your cleanup logic here
        pass

    @hookimpl
    def lifecycle_on_game_added(self, game: dict) -> None:
        """Called when a new game is added to any library.

        Args:
            game: dict with game info (id, title, slug, source, ...)
        """
        # TODO: react to new games
        # Example: send a Discord webhook, update a spreadsheet, etc.
        logger.info("Game added: %s", game.get("title", "?"))

    @hookimpl
    def lifecycle_on_download_complete(self, game: dict, path: str) -> None:
        """Called when a game download finishes.

        Args:
            game: dict with game info
            path: filesystem path to the downloaded file
        """
        # TODO: post-download processing
        # Example: scan with antivirus, notify user, move file, etc.
        logger.info("Download complete: %s -> %s", game.get("title", "?"), path)
