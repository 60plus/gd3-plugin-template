# GD3 Plugin Template

Templates and examples for building plugins for [GamesDownloader V3](https://gitea.domowy.tech/60plus/GamesDownloader).

## What can plugins do?

| Type | Description | Example |
|------|-------------|---------|
| **metadata** | Scrape game info from external sources (descriptions, ratings, screenshots) | PPE.pl scraper |
| **download** | Add new download sources | Torrent tracker integration |
| **library** | Scan game libraries from new sources | NAS folder scanner |
| **theme** | Add custom themes, skins, and layouts | NEON HORIZON theme |
| **widget** | Add dashboard cards and widgets | RSS feed reader |
| **lifecycle** | Hook into app events (game added, download complete, startup/shutdown) | Discord notifier |

## Quick start

1. Copy a template from `templates/` matching your plugin type
2. Edit `plugin.json` with your plugin info
3. Write your code in `plugin.py`
4. ZIP the folder and install via Settings > Plugins in GamesDownloader

```
my-plugin/
  plugin.json       # manifest (required)
  plugin.py         # entry point with Plugin class (required)
  logo.png          # icon shown in Settings (optional)
  requirements.txt  # pip dependencies (optional)
  README.md         # documentation (optional)
```

## Plugin manifest (plugin.json)

Every plugin needs a `plugin.json` in its root:

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
      "label": "Enable plugin"
    }
  }
}
```

### Required fields

| Field | Description |
|-------|-------------|
| `id` | Unique identifier, lowercase with dashes (e.g. `my-scraper`) |
| `name` | Display name shown in Settings |
| `version` | Semantic version (e.g. `1.0.0`) |
| `author` | Your name or handle |
| `type` | One of: `metadata`, `download`, `library`, `theme`, `widget`, `lifecycle` |
| `entry` | Python file containing the `Plugin` class (usually `plugin.py`) |

### Optional fields

| Field | Description |
|-------|-------------|
| `description` | Short description shown in Settings |
| `requires` | List of pip package names needed by the plugin |
| `min_gd_version` | Minimum GamesDownloader version required |
| `config_schema` | Configuration fields (rendered as form in Settings > Plugins) |

### Config schema types

| Type | Renders as | Properties |
|------|-----------|------------|
| `boolean` | Toggle switch | `default` |
| `string` | Text input | `default` |
| `number` | Number input | `default` |
| `select` | Dropdown | `default`, `options` (array of strings) |

## Plugin class

Your `plugin.py` must define a `Plugin` class that implements hooks:

```python
from plugins.hookspecs import hookimpl

class Plugin:
    @hookimpl
    def metadata_provider_name(self) -> str:
        return "My Source"

    @hookimpl
    def metadata_provider_id(self) -> str:
        return "mysource"
```

## Available hooks

See [docs/HOOKS.md](docs/HOOKS.md) for the full hook reference.

## Installing plugins

1. Go to **Settings > Plugins** in GamesDownloader
2. Drag and drop your `.zip` file into the install area
3. The plugin is extracted, dependencies installed, and loaded automatically
4. Enable/disable and configure from the same page

## Building a ZIP

```bash
cd my-plugin/
zip -r ../my-plugin-v1.0.0.zip .
```

## Directory structure

```
gd3-plugin-template/
  templates/
    metadata-scraper/   # starter template for metadata plugins
    theme/              # starter template for theme plugins
    widget/             # starter template for widget plugins
  examples/
    ppe-metadata/       # complete PPE.pl scraper (descriptions, ratings, screenshots)
    gd3-translator/     # complete translator (26 languages, chunked translation)
    neon-horizon/       # complete theme plugin (8 skins, particles, neon glow)
  dist/
    ppe-metadata-v1.0.0.zip       # ready-to-install PPE.pl plugin
    gd3-translator-v1.0.0.zip     # ready-to-install translator plugin
    neon-horizon-v1.0.0.zip       # ready-to-install NEON HORIZON theme
  docs/
    HOOKS.md            # detailed hook reference
  build.sh              # ZIP packaging helper
```

## Examples

### PPE.pl Metadata Scraper (`examples/ppe-metadata/`)

A complete metadata plugin that scrapes game data from PPE.pl (Polish gaming website):

- Searches via PPE.pl native API (`/api/search?search=...&type=game`)
- Scrapes Polish descriptions, ratings (x/10), genres, release dates, developers
- Extracts full screenshot galleries (parses `data-elements` JSON from PPE gallery widget)
- Ratings persisted to DB (fetched once, cached permanently)
- Screenshots shown as source in Edit Metadata panel with PPE.pl icon
- Includes plugin logo (orange P icon)
- Config: search engine selector, minimum match score threshold

**Plugin type:** `metadata` (implements `MetadataProviderSpec`)

### Description Translator (`examples/gd3-translator/`)

Translates game descriptions between languages using Google Translate:

- Uses `translate-shell` Python package (no API key needed)
- 26 languages supported with emoji flag display on the translate button
- Long texts split into chunks at paragraph boundaries (450 char limit per chunk)
- Runs in a separate thread to avoid asyncio conflicts with FastAPI
- Translate button appears next to Full Description and Short Description fields in Edit Metadata
- Config: source language (default: English), target language (default: Polish)

**Plugin type:** `lifecycle` (translation exposed via `/api/plugins/translate` endpoint)

### NEON HORIZON Theme (`examples/neon-horizon/`)

A futuristic theme with animated gradients, floating particles, glass morphism, and neon glow effects:

- **8 skins:** 4 solid (Cyan Flux, Violet Surge, Magenta Pulse, Gold Circuit) + 4 dual-color gradient (Cyber, Plasma, Sunset, Aurora)
- **Typography:** Orbitron for headings, Rajdhani for body text
- **Animated background:** Radial gradient with hue-rotate shift animation
- **CSS-only floating particles:** Two layers of animated dots for depth
- **Neon glow effects:** Configurable intensity on cards, text, buttons, and panels
- **Glass morphism:** Enhanced shadows with inset highlights
- **Scanline overlay:** Optional CRT-style horizontal lines (toggle in settings)
- **Couch Mode:** 3D perspective glow on carousel cards, gradient ROM count badges
- **5 configurable settings:** Particle Count, Neon Glow intensity, Glass Blur, Scanline Overlay, BG Animation Speed

**Plugin type:** `theme` (implements `FrontendProviderSpec`)

## Ready-to-install ZIPs

The `dist/` folder contains pre-built ZIP files you can install directly:

| Plugin | File | Description |
|--------|------|-------------|
| PPE.pl Scraper | `dist/ppe-metadata-v1.0.0.zip` | Polish game metadata (descriptions, ratings, screenshots) |
| Translator | `dist/gd3-translator-v1.0.0.zip` | Translate descriptions between 26 languages |
| NEON HORIZON | `dist/neon-horizon-v1.0.0.zip` | Futuristic theme with particles, neon glow, 8 skins |

Install via **Settings > Plugins** in GamesDownloader - drag and drop the ZIP file.

## License

MIT
