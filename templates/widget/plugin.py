"""Widget plugin template.

Adds custom cards to the GamesDownloader dashboard.
"""

from __future__ import annotations

from plugins.hookspecs import hookimpl


class Plugin:
    """Widget provider - implements WidgetSpec hooks."""

    @hookimpl
    def widget_get_cards(self) -> list[dict] | None:
        """Return a list of dashboard card definitions.

        Each card is a small data tile rendered on the core Dashboard page.
        The server keeps exactly these fields (anything else is dropped):
          - id: str        unique card id (falls back to title if omitted)
          - title: str     card header
          - value: str     the big value/number shown on the card (optional)
          - subtitle: str  small caption under the value (optional)
          - icon: str      a Material Design Icon name, e.g. "mdi-controller"
                           (NOT an image URL) (optional)
          - link: str      in-app path the card navigates to on click,
                           e.g. "/x/my-page" (optional)
        """
        return [
            {
                "id": "my-stat",
                "title": "My Plugin",
                "value": "42",
                "subtitle": "things tracked",
                "icon": "mdi-chart-box",
                "link": "/x/my-page",
            }
        ]
