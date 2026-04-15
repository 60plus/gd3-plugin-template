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

### Theme Plugin Architecture

Theme plugins provide three hook implementations:

```python
from plugins.hookspecs import hookimpl
from pathlib import Path

class Plugin:
    @hookimpl
    def frontend_get_theme(self):
        return {
            "id": "neon-horizon",
            "name": "NEON HORIZON",
            "layout": "neon-horizon",
            "skins": [
                {"id": "nh-cyber", "name": "Cyan Flux", "preview": "#00d4ff"},
                {"id": "nh-violet", "name": "Violet Surge", "preview": "#8b5cf6"},
            ],
            "defaultSkin": "nh-cyber",
            "cssFile": "neon-horizon",
            # Google Fonts URL - loaded as a <link> in <head>, makes the font
            # available for use in your CSS (e.g. font-family: 'Orbitron')
            "font": "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap",
            "settings": [
                {
                    "key": "particleCount",
                    "label": "nh.setting_particles",
                    "hint": "nh.setting_particles_hint",
                    "type": "select",
                    "default": "6",
                    "options": ["0", "3", "6", "12"],
                    # optionLabels can be i18n keys - the Settings UI translates them
                    "optionLabels": ["nh.opt_none", "nh.opt_few", "nh.opt_normal", "nh.opt_many"],
                    "cssVar": "--nh-particle-count",
                },
            ],
        }

    @hookimpl
    def frontend_get_css(self):
        return Path(__file__).parent.joinpath("neon-horizon.css").read_text(encoding="utf-8")

    @hookimpl
    def frontend_get_js(self):
        return Path(__file__).parent.joinpath("neon-horizon.js").read_text(encoding="utf-8")
```

### Vue SFC Compilation

Theme plugins with `.vue` files are compiled on container startup by Vite:

1. Plugin has `.vue` files + `plugin.json` with `"type": "theme"`
2. Container entrypoint runs `compile-theme-plugins.mjs`
3. Vite compiles to IIFE bundle: `layout.js` + `layout.css`
4. Frontend loads and registers components via `window.__GD__`

**After installing/updating a theme plugin, restart the container** (Plugin Store has a "Restart Now" button).

### Component Naming Convention

Vue file names must follow a specific naming convention based on the layout ID in your theme definition:

- Layout ID `"my-theme"` maps to `MyThemeLayout.vue` (main layout shell)
- Layout ID `"my-theme"` maps to `MyThemeCouch.vue` (couch mode component)

The conversion is kebab-case to PascalCase plus the suffix (`Layout` or `Couch`). Examples:

| Layout ID | Layout File | Couch File |
|-----------|-------------|------------|
| `neon-horizon` | `NeonHorizonLayout.vue` | `NeonHorizonCouch.vue` |
| `retro-wave` | `RetroWaveLayout.vue` | `RetroWaveCouch.vue` |
| `minimal` | `MinimalLayout.vue` | `MinimalCouch.vue` |

The compiler scans for `*Layout.vue` and `*Couch.vue` files automatically. You do not need to register them manually.

### Auto-Registration

Compiled Vue plugins auto-register their layout and couch components - you do not need to call `registerPluginLayout()` or `registerPluginCouchMode()` manually. The Vite compiler handles this during the build step. Only raw JS plugins (non-Vue) need manual registration.

### Vue Files - Important Rules

Plugin `.vue` files are compiled **outside the main app bundle**. You cannot use `@/` imports. Instead use `window.__GD__`:

```typescript
// Vue runtime - import normally
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// GD runtime - access via window.__GD__
const _gd = (window as any).__GD__
const client = _gd.api                        // Axios with Bearer token
const auth = _gd.stores.auth()                 // { user } - token hidden
const themeStore = _gd.stores.theme()          // full theme store
const t = _gd.i18n?.t || ((k: string) => k)   // i18n translation

// Couch Mode composables
const { useCouchNav, couchNavPaused } = _gd.composables
const getEjsCore = _gd.getEjsCore             // platform -> EmulatorJS core

// Notifications - push badges to user avatar
_gd.notifications.add({ id: 'my-alert', count: 1, label: 'Something happened', action: '/settings' })
_gd.notifications.dismiss('my-alert')
```

**Global components** available in templates:
- `<DownloadManager />` - Download queue tray (admin only)
- `<RandomGamePicker />` - Random game dice button
- `<AmbientBackground />` - Animated orb background

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

You can also load JSON data from assets via the API client:
```typescript
const { data } = await client.get('/api/plugins/neon-horizon/assets/platforms.json')
// data is the parsed JSON object
```

### data-theme and data-skin CSS Selectors

When a theme is active, GD sets `data-theme` and `data-skin` attributes on the `<html>` element. Use these to scope your CSS:

```css
/* Target your theme specifically */
[data-theme="my-theme"] {
  --my-bg: #0a0a1a;
  --my-accent: #00d4ff;
}

/* Target a specific skin within your theme */
[data-theme="my-theme"][data-skin="sunset"] {
  --my-accent: #f97316;
}

/* Skin-only selector (also works) */
[data-skin="nh-cyber"] {
  --pl: #00d4ff;
  --pl-light: #67e8f9;
}
```

This ensures your styles only apply when your theme/skin is active and don't leak into other themes.

### Theme Settings

Settings in `frontend_get_theme()` -> `settings[]` are:
- Rendered in Settings > Appearance > Theme Settings
- Applied as CSS custom properties on `:root`
- Setting types: `range` (slider), `select` (chips), `toggle` (on/off)
- Labels and hints support i18n keys: use `"label": "nh.my_setting"` and define the key in your plugin's `i18n.json`
- For `range` type: the `"unit"` field (e.g. `"px"`, `"deg"`) is appended to the value when setting the CSS variable. So value `30` with unit `"px"` produces `--my-var: 30px`
- For `select` type: `"optionLabels"` can be i18n keys (e.g. `["nh.opt_none", "nh.opt_few"]`) - the Settings UI translates them automatically

### frontend_get_js() Patterns

The `frontend_get_js()` hook returns a JavaScript string injected into `<head>`. Since it runs in the global scope, wrap your code in an IIFE to avoid polluting the global namespace:

```javascript
(function() {
  'use strict';

  // Helper to read CSS variables set by theme settings
  function getCssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  // React to theme setting changes (slider moved, toggle flipped, etc.)
  document.documentElement.addEventListener('gd-theme-updated', () => {
    const blur = getCssVar('--my-glass-blur');
    const particles = getCssVar('--my-particle-count');
    // Update your JS effects based on new values
  });

  // Use MutationObserver to react to DOM changes (SPA route changes, new elements)
  const observer = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const node of m.addedNodes) {
        if (node.nodeType === 1) {
          // Process newly added elements
        }
      }
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

  // Poll CSS variables for initial values (useful on page load)
  const count = parseInt(getCssVar('--my-particle-count') || '6', 10);
})();
```

### i18n in Plugins

Plugins provide their own translations via an `i18n.json` file in the plugin root. This file is auto-loaded by the app at startup via `GET /api/plugins/frontend/i18n`, which merges translations from all installed plugins.

**i18n.json format:**

```json
{
  "en": {
    "nh.setting_particles": "Particle Count",
    "nh.setting_particles_hint": "Number of floating particles",
    "nh.opt_none": "None",
    "nh.opt_few": "Few",
    "nh.opt_normal": "Normal",
    "nh.opt_many": "Many",
    "nh.home_title": "Welcome",
    "nh.library_empty": "No games found"
  },
  "pl": {
    "nh.setting_particles": "Liczba czastek",
    "nh.setting_particles_hint": "Ilosc unoszczych sie czastek",
    "nh.opt_none": "Brak",
    "nh.opt_few": "Malo",
    "nh.opt_normal": "Normalnie",
    "nh.opt_many": "Duzo",
    "nh.home_title": "Witaj",
    "nh.library_empty": "Nie znaleziono gier"
  }
}
```

Use a unique prefix for all your keys (e.g. `nh.*`, `retro.*`) to avoid collisions with other plugins.

**Using translations in Vue components:**
```typescript
const t = _gd.i18n?.t || ((k: string) => k)
// t('nh.home_title') -> "Welcome" (en) or "Witaj" (pl)
```

**Using translations in theme settings:**

Setting `label`, `hint`, and `optionLabels` fields can reference i18n keys directly. The Settings UI translates them automatically:
```python
"settings": [{
    "label": "nh.setting_particles",       # translated by Settings UI
    "hint": "nh.setting_particles_hint",   # translated by Settings UI
    "optionLabels": ["nh.opt_none", "nh.opt_few"],  # each label translated
}]
```

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
