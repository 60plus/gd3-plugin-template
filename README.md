# GD3 Plugin Development Guide

Templates, examples, and documentation for building plugins for [GamesDownloader V3](https://github.com/60plus/GamesDownloader).

> **Looking to install plugins?** Go to [gd3-plugin-store](https://github.com/60plus/gd3-plugin-store) for ready-to-install ZIPs, or add the store URL in Settings > Plugin Store.

---

## Plugin Types

| Type | Description | Hooks | Example |
|------|-------------|-------|---------|
| **theme** | Custom layouts, Vue components, CSS, JS, couch mode | `FrontendProviderSpec` | NEON HORIZON |
| **metadata** | Scrape game info from external sources | `MetadataProviderSpec` | PPE.pl Scraper |
| **lifecycle** | Hook into app events (startup, game added, download done) | `LifecycleSpec` | Description Translator |
| **download** | Add new download sources | `DownloadProviderSpec` | - |
| **library** | Scan game libraries from new sources | `LibrarySourceSpec` | - |
| **widget** | Add dashboard cards | `WidgetSpec` | - |

---

## Quick Start

1. Copy a starter template from `templates/` matching your plugin type
2. Edit `plugin.json` with your plugin info
3. Implement hooks in `plugin.py`
4. ZIP the folder and install via Settings > Plugins

```
my-plugin/
  plugin.json       # manifest (required)
  plugin.py         # Python class with @hookimpl methods (required)
  logo.png          # icon shown in Settings (optional, auto-detected)
  requirements.txt  # pip dependencies, installed automatically (optional)
  i18n.json         # plugin translations (optional, theme/lifecycle plugins)
```

---

## plugin.json Manifest

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "What this plugin does",
  "type": "metadata",
  "entry": "plugin.py",
  "requires": ["httpx", "beautifulsoup4"],
  "min_gd_version": "3.0.0",
  "config_schema": {
    "api_key": {
      "type": "string",
      "default": "",
      "label": "API Key"
    },
    "enabled": {
      "type": "boolean",
      "default": true,
      "label": "Enable"
    }
  }
}
```

Config schema fields are rendered as a settings form in Settings > Plugins. Supported types: `string`, `number`, `boolean`, `select`.

> **config_schema vs theme settings:** Theme plugins use `frontend_get_theme().settings[]` for appearance settings (blur, particles, colors) - these are rendered in Settings > Appearance > Theme Settings. The `config_schema` in plugin.json is for plugin configuration (rendered in Settings > Plugins). Theme plugins typically have empty `"config_schema": {}`.

---

## Plugin Class & Hooks

Your `plugin.py` must define a `Plugin` class using `@hookimpl` decorators:

```python
from plugins.hookspecs import hookimpl

class Plugin:
    @hookimpl
    def metadata_provider_name(self) -> str:
        return "My Source"

    @hookimpl
    def metadata_provider_id(self) -> str:
        return "my-source"
```

See [docs/HOOKS.md](docs/HOOKS.md) for the full hook reference with all specs and return types.

---

## Example: Metadata Plugin (PPE.pl Scraper)

**Source:** `examples/ppe-metadata/`

A metadata scraper that finds Polish game descriptions, ratings, genres, and screenshots from PPE.pl.

**How it works:**
1. `metadata_search_game(query)` searches PPE.pl via Bing/DuckDuckGo, returns matching pages
2. `metadata_get_game(url)` scrapes the page with BeautifulSoup, extracts structured data
3. `metadata_get_cover_url(url)` extracts the game cover image URL
4. Fuzzy title matching with configurable threshold (default 65%)

**Hooks implemented:** `MetadataProviderSpec`
- `metadata_provider_name()` / `metadata_provider_id()` - identity
- `metadata_search_game(query)` - search PPE.pl, return `[{provider_id, provider_game_id, name, snippet}]`
- `metadata_get_game(provider_game_id)` - scrape full metadata: title, description, rating (0-100), genre, release_date, developer, screenshots, source_url
- `metadata_get_cover_url(provider_game_id)` - cover image URL

**Config:** search engine (bing/duckduckgo), minimum match score

**Dependencies:** `beautifulsoup4`, `httpx`

**Files:**
```
ppe-metadata/
  plugin.json        # manifest, type: metadata
  plugin.py          # 450 lines - search + scrape + fuzzy match
  logo.png           # plugin icon
  requirements.txt   # beautifulsoup4, httpx
```

---

See [docs/HOOKS.md](docs/HOOKS.md) for the full hook reference, more examples, and theme plugin architecture.

---

## Distribution

To distribute your plugin:

1. ZIP your plugin folder: `cd my-plugin && zip -r ../my-plugin-v1.0.0.zip .`
2. Users install via Settings > Plugins (drag & drop ZIP)
3. Or publish to a Plugin Store - see [gd3-plugin-store](https://github.com/60plus/gd3-plugin-store) for the store.json format

---

## License

MIT (plugin template code). Theme assets may have separate licenses - see credits in HOOKS.md.
