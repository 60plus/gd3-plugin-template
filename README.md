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

See [docs/HOOKS.md](docs/HOOKS.md) for all examples including PPE.pl Scraper, Description Translator, and NEON HORIZON Theme with full architecture documentation.

---

## Starter Templates

| Template | Path | Description |
|----------|------|-------------|
| Metadata Scraper | `templates/metadata-scraper/` | Search + fetch game data from external source |
| Theme | `templates/theme/` | Custom layout with CSS, JS, and settings |
| Lifecycle | `templates/lifecycle/` | Hook into app events, register custom endpoints |
| Widget | `templates/widget/` | Dashboard card with custom content |

Each template has a `plugin.py` with TODO comments showing where to add your code.

---

## Distribution

To distribute your plugin:

1. ZIP your plugin folder: `cd my-plugin && zip -r ../my-plugin-v1.0.0.zip .`
2. Users install via Settings > Plugins (drag & drop ZIP)
3. Or publish to a Plugin Store - see [gd3-plugin-store](https://github.com/60plus/gd3-plugin-store) for the store.json format

---

## Credits & Acknowledgments

GamesDownloader V3 and its plugin system were inspired by several outstanding open-source projects:

- **[RomM](https://github.com/rommapp/romm)** - ROM management platform that inspired the emulation library architecture, metadata scraping approach, and platform organization
- **[Gameyfin](https://github.com/grimsi/gameyfin)** - Self-hosted game library manager that inspired the original concept of a personal game vault with automatic metadata fetching

NEON HORIZON Couch Mode uses assets from EmulationStation themes by [RobZombie9043](https://github.com/RobZombie9043):

- **[Colorful Pop](https://github.com/RobZombie9043/colorful-pop-es-de)** - Platform artwork, SVG logos, colored icons, platform metadata with 15-language descriptions, video positioning data, and system color palettes
- **[Elementerial](https://github.com/RobZombie9043/elementerial-es-de)** - Additional design inspiration

These EmulationStation themes are licensed under **Creative Commons CC-BY-NC-SA**. The assets are included for non-commercial, personal use. All credit for original artwork goes to RobZombie9043.

Special thanks to the teams behind [EmulatorJS](https://emulatorjs.org/), [ScreenScraper](https://www.screenscraper.fr/), [SteamGridDB](https://www.steamgriddb.com/), and [HowLongToBeat](https://howlongtobeat.com/) for their APIs and services.

## License

MIT (plugin template code). Theme assets may have separate licenses - see credits above.
