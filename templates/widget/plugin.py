"""Widget plugin template.

Adds custom cards to the GamesDownloader dashboard.
"""

from __future__ import annotations

from plugins.hookspecs import hookimpl


class Plugin:
    """Widget provider - implements WidgetSpec hooks."""

    @hookimpl
    def widget_get_cards(self) -> list[dict] | None:
        """Return a list of widget card definitions.

        Each card dict can include:
          - title: str (card header)
          - content: str (HTML content)
          - icon: str (optional icon URL)
          - link: str (optional link URL)
          - order: int (sort order, lower = first)
        """
        return [
            {
                "title": "My Widget",
                "content": "<p>Hello from my plugin!</p>",
                "order": 100,
            }
        ]
