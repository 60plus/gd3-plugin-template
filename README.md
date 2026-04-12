# GD3 Plugin Development Guide

Templates, examples, and documentation for building plugins for [GamesDownloader V3](https://gitea.domowy.tech/60plus/GamesDownloader).

> **Looking to install plugins?** Go to [gd3-plugin-store](https://gitea.domowy.tech/60plus/gd3-plugin-store) for ready-to-install ZIPs, or add the store URL in Settings > Plugin Store.

---

## Plugin Types

| Type | Description | Hooks | Example |
|------|-------------|-------|---------|
| **theme** | Custom layouts, Vue components, CSS, JS, couch mode | `FrontendProviderSpec` | NEON HORIZON |
| **metadata** | Scrape game info from external sources | `MetadataProviderSpec` | PPE.pl Scraper |
| **lifecycle** | Hook into app events (startup, game added, download done) | `LifecycleSpec` | Description Translator |
| **download** | Add new download sources | `DownloadProviderSpec` | — |
| **library** | Scan game libraries from new sources | `LibrarySourceSpec` | — |
| **widget** | Add dashboard cards | `WidgetSpec` | — |

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
```

---

## plugin.json Manifest

```json
{
  \"id\": \"my-plugin\",
  \"name\": \"My Plugin\",
  \"version\": \"1.0.0\",
  \"author\": \"Your Name\",
  \"description\": \"What this plugin does\",
  \"type\": \"metadata\",
  \"entry\": \"plugin.py\",
  \"has_logo\": true,
  \"requires\": [\"httpx\", \"beautifulsoup4\"],
  \"min_gd_version\": \"3.0.0\",
  \"config_schema\": {
    \"api_key\": {
      \"type\": \"string\",
      \"default\": \"\",
      \"label\": \"API Key\"
    },
    \"enabled\": {
      \"type\": \"boolean\",
      \"default\": true,
      \"label\": \"Enable\"
    }
  }
}
```

Config schema fields are rendered as a settings form in Settings > Plugins. Supported types: `string`, `number`, `boolean`, `select`.

---

## Plugin Class & Hooks

Your `plugin.py` must define a `Plugin` class using `@hookimpl` decorators:

```python
from plugins.hookspecs import hookimpl

class Plugin:
    @hookimpl
    def metadata_provider_name(self) -> str:
        return \"My Source\"

    @hookimpl
    def metadata_provider_id(self) -> str:
        return \"my-source\"
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
- `metadata_provider_name()` / `metadata_provider_id()` — identity
- `metadata_search_game(query)` — search PPE.pl, return `[{provider_id, provider_game_id, name, snippet}]`
- `metadata_get_game(provider_game_id)` — scrape full metadata: title, description, rating (0-100), genre, release_date, developer, screenshots, source_url
- `metadata_get_cover_url(provider_game_id)` — cover image URL

**Config:** search engine (bing/duckduckgo), minimum match score

**Dependencies:** `beautifulsoup4`, `httpx`

**Files:**
```
ppe-metadata/
  plugin.json        # manifest, type: metadata
  plugin.py          # 450 lines — search + scrape + fuzzy match
  logo.png           # plugin icon
  requirements.txt   # beautifulsoup4, httpx
```

---

## Example: Lifecycle Plugin (Description Translator)

**Source:** `examples/gd3-translator/`

Translates game descriptions between 26 languages using Google Translate (via translate-shell).

**How it works:**
1. Backend exposes `/api/plugins/translate` endpoint
2. Frontend adds a translate button on game detail pages
3. Text is split into ~450-char chunks at paragraph boundaries
4. Each chunk translated via `translate-shell` package
5. Results joined back together

**Hooks implemented:** `LifecycleSpec`
- `lifecycle_on_startup()` — registers the translate endpoint

**Key patterns:**
- Async-safe threading: uses `asyncio.to_thread()` to avoid blocking the event loop
- Text chunking: splits at `\\n\\n` boundaries, respects max chunk size
- Language detection: `from_lang: \"auto\"` uses Google's auto-detect

**Config:** source language (auto/en/pl/de/...), target language

**Dependencies:** `translate-shell>=0.0.59`

**Files:**
```
gd3-translator/
  plugin.json        # manifest, type: lifecycle
  plugin.py          # 140 lines — translate endpoint + chunking
  logo.png           # plugin icon
  requirements.txt   # translate-shell
```

---

## Example: Theme Plugin (NEON HORIZON)

**Source:** `examples/neon-horizon/`

A complete cyberpunk theme with custom Vue layouts, Colorful Pop couch mode, 8 color skins, and gamepad support. This is the most complex plugin type — study it to understand the full capabilities.

### Theme Plugin Architecture

Theme plugins provide three hook implementations:

```python
from plugins.hookspecs import hookimpl
from pathlib import Path

class Plugin:
    @hookimpl
    def frontend_get_theme(self):
        return {
            \"id\": \"neon-horizon\",
            \"name\": \"NEON HORIZON\",
            \"layout\": \"neon-horizon\",          # must match registerPluginLayout() id
            \"skins\": [
                {\"id\": \"nh-cyber\", \"name\": \"Cyan Flux\", \"preview\": \"#00d4ff\"},
                {\"id\": \"nh-violet\", \"name\": \"Violet Surge\", \"preview\": \"#8b5cf6\"},
            ],
            \"defaultSkin\": \"nh-cyber\",
            \"cssFile\": \"neon-horizon\",
            \"font\": \"https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap\",
            \"settings\": [
                {
                    \"key\": \"particleCount\",
                    \"label\": \"nh.setting_particles\",    # i18n key (translated in Settings UI)
                    \"hint\": \"nh.setting_particles_hint\",
                    \"type\": \"select\",
                    \"default\": \"6\",
                    \"options\": [\"0\", \"3\", \"6\", \"12\"],
                    \"optionLabels\": [\"nh.opt_none\", \"nh.opt_few\", \"nh.opt_normal\", \"nh.opt_many\"],
                    \"cssVar\": \"--nh-particle-count\",
                },
            ],
        }

    @hookimpl
    def frontend_get_css(self):
        return Path(__file__).parent.joinpath(\"neon-horizon.css\").read_text(encoding=\"utf-8\")

    @hookimpl
    def frontend_get_js(self):
        return Path(__file__).parent.joinpath(\"neon-horizon.js\").read_text(encoding=\"utf-8\")
```

### Vue SFC Compilation

Theme plugins with `.vue` files are compiled on container startup by Vite:

1. Plugin has `.vue` files + `plugin.json` with `\"type\": \"theme\"`
2. Container entrypoint runs `compile-theme-plugins.mjs`
3. Vite compiles to IIFE bundle: `layout.js` + `layout.css`
4. Frontend loads and registers components via `window.__GD__`

**After installing/updating a theme plugin, restart the container** (Plugin Store has a \"Restart Now\" button).

### Vue Files — Important Rules

Plugin `.vue` files are compiled **outside the main app bundle**. You cannot use `@/` imports. Instead use `window.__GD__`:

```typescript
// Vue runtime — import normally
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// GD runtime — access via window.__GD__
const _gd = (window as any).__GD__
const client = _gd.api                        // Axios with Bearer token
const auth = _gd.stores.auth()                 // { user } — token hidden
const themeStore = _gd.stores.theme()          // full theme store
const t = _gd.i18n?.t || ((k: string) => k)   // i18n translation

// Couch Mode composables
const { useCouchNav, couchNavPaused } = _gd.composables
const getEjsCore = _gd.getEjsCore             // platform → EmulatorJS core

// Register your layout + couch components
_gd.registerPluginLayout('my-theme', LayoutComponent)
_gd.registerPluginCouchMode('my-theme', CouchComponent)
```

**Global components** available in templates:
- `<DownloadManager />` — Download queue tray (admin only)
- `<RandomGamePicker />` — Random game dice button
- `<AmbientBackground />` — Animated orb background

### Plugin Assets

Static files in `assets/` are served at:
```
/api/plugins/{plugin-id}/assets/{path}
```

Helper pattern:
```typescript
const PLUGIN_ID = 'neon-horizon'
function pluginAsset(path: string): string {
  return `/api/plugins/${PLUGIN_ID}/assets/${path}`
}
```

### Theme Settings

Settings in `frontend_get_theme()` → `settings[]` are:
- Rendered in Settings > Appearance > Theme Settings
- Applied as CSS custom properties on `:root`
- Setting types: `range` (slider), `select` (chips), `toggle` (on/off)
- Labels support i18n keys: use `\"label\": \"nh.my_setting\"` and add the key to the app's i18n files

### i18n in Plugins

Use the main app's i18n system:
```typescript
const t = _gd.i18n?.t || ((k: string) => k)
// t('nh.my_key') → translated string, falls back to key
```

Add your keys to the main app's `frontend/src/i18n/en.json` and `pl.json` with a plugin prefix (e.g. `nh.*`).

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
  plugin.py                # Theme definition — skins, settings, CSS/JS hooks
  plugin.json              # Manifest
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
| Widget | `templates/widget/` | Dashboard card with custom content |

Each template has a `plugin.py` with TODO comments showing where to add your code.

---

## Distribution

To distribute your plugin:

1. ZIP your plugin folder: `cd my-plugin && zip -r ../my-plugin-v1.0.0.zip .`
2. Users install via Settings > Plugins (drag & drop ZIP)
3. Or publish to a Plugin Store — see [gd3-plugin-store](https://gitea.domowy.tech/60plus/gd3-plugin-store) for the store.json format

---

## Credits & Acknowledgments

NEON HORIZON Couch Mode is inspired by and uses assets from EmulationStation themes by [RobZombie9043](https://github.com/RobZombie9043):

- **[Colorful Pop](https://github.com/RobZombie9043/colorful-pop-es-de)** — Platform artwork, SVG logos, colored icons, platform metadata with 15-language descriptions, video positioning data, and system color palettes
- **[Elementerial](https://github.com/RobZombie9043/elementerial-es-de)** — Additional design inspiration

These EmulationStation themes are licensed under **Creative Commons CC-BY-NC-SA**. The assets are included for non-commercial, personal use. All credit for original artwork goes to RobZombie9043.

## License

MIT (plugin template code). Theme assets may have separate licenses — see credits above.
