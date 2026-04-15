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
  logo.png          # icon shown in Settings (optional)
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

## Example: Lifecycle Plugin (Description Translator)

**Source:** `examples/gd3-translator/`

Translates game descriptions between 26 languages using Google Translate (via translate-shell).

**How it works:**
1. GD backend has a built-in `/api/plugins/translate` endpoint that calls `translate_text()` from this plugin
2. Frontend shows a translate button on game detail pages
3. Plugin splits long text into ~450-char chunks at `\n` paragraph boundaries
4. Each chunk is translated via `translate-shell` package in a separate thread
5. Results are joined back together and returned

**Hooks implemented:** `LifecycleSpec`
- `lifecycle_on_startup()` - logs that the plugin is loaded (the translate endpoint is provided by GD's plugins_router, not registered by the plugin itself)

**Key patterns:**
- Thread-safe translation: uses `concurrent.futures.ThreadPoolExecutor` because `translate-shell` internally calls `asyncio.run()` which conflicts with FastAPI's event loop
- Text chunking: splits at `\n` boundaries, max ~450 chars per chunk
- Language detection: `from_lang: "auto"` uses Google's auto-detect
- Return format: `{"ok": bool, "text": str, "from_lang": str, "to_lang": str, "error": str}`

**Config (Settings > Plugins > Translator):**
- `from_lang` - source language (select, 26 options including "auto")
- `to_lang` - target language (select, 26 options)
- Uses `config_schema` with `select` type - rendered as dropdown in plugin settings

**Dependencies:** `translate-shell>=0.0.59`

**Files:**
```
gd3-translator/
  plugin.json        # manifest, type: lifecycle, config_schema with select fields
  plugin.py          # 140 lines - translate function + chunking logic
  logo.png           # plugin icon
  requirements.txt   # translate-shell
```

---

## Example: Theme Plugin (NEON HORIZON)

**Source:** `examples/neon-horizon/`

A complete cyberpunk theme with custom Vue layouts, Colorful Pop couch mode, 8 color skins, and gamepad support. This is the most complex plugin type - study it to understand the full capabilities.

**Key features (v1.2.5):**
- Netflix-style home page with hero banner and recently added rows
- Steam Big Picture library views (16:9 landscape cards)
- Colorful Pop couch mode with platform carousel, video playback in TV cutouts, favorites and recently played
- Per-game platform color in favorites/recent (reads platform color from platforms.json)
- Locale-aware platform descriptions (reads UI language from localStorage, falls back to English)
- Notification badge support (polls `__GD__.notifications.store` for update badges on avatar)
- Full i18n via i18n.json (58 keys EN+PL)
- 8 color skins (4 solid + 4 dual-gradient)
- Configurable settings: particle count, glass blur, glass opacity, scanline overlay

See [docs/HOOKS.md](docs/HOOKS.md) for the full theme plugin architecture documentation including Vue SFC compilation, component naming, CSS selectors, settings, i18n, and the `window.__GD__` API reference.

**NEON HORIZON Files:**
```
neon-horizon/
  NeonHorizonLayout.vue    # Main shell (navbar, particles, route detection)
  NeonHorizonHome.vue      # Home page (hero banner, recently added rows)
  NeonHorizonLibrary.vue   # Library view (Big Picture cards, alphabet sidebar)
  NeonHorizonSearch.vue    # Global search results
  NeonHorizonCouch.vue     # Couch Mode (Colorful Pop style, 1000+ lines)
  neon-horizon.css         # CSS overrides for existing GD components
  neon-horizon.js          # Dynamic effects (gradient text, glass blur observer)
  plugin.py                # Theme definition - skins, settings, CSS/JS hooks
  plugin.json              # Manifest
  i18n.json                # Plugin translations (en + pl)
  logo.svg                 # Plugin icon
  assets/
    pop/                   # Pop character artwork per platform (95 platforms)
    overlay/               # Console overlay with TV cutout (RGBA transparency)
    artwork/               # Modern console artwork (Ken Burns background)
    icons/                 # Colored platform icons
    logos/                 # SVG platform name logos
    platforms.json         # Platform metadata (names, colors, descriptions in 15 languages)
    videopos.json          # Video positions inside TV cutouts
```

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
