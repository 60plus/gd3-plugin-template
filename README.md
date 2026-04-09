# GD3 Plugin Template

Templates and examples for building plugins for [GamesDownloader V3](https://gitea.domowy.tech/60plus/GamesDownloader).

## What can plugins do?

| Type | Description | Example |
|------|-------------|---------|
| **metadata** | Scrape game info from external sources (descriptions, ratings, screenshots) | PPE.pl scraper |
| **download** | Add new download sources | Torrent tracker integration |
| **library** | Scan game libraries from new sources | NAS folder scanner |
| **theme** | Complete custom themes with layouts, couch mode, and visual effects | NEON HORIZON theme |
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

---

## Building a Theme Plugin

Theme plugins can provide **complete custom layouts** — not just color skins. The plugin system compiles Vue SFC files on container startup, giving you full control over HTML structure, CSS, and interactivity.

### What theme plugins can provide

| Component | File | Description |
|-----------|------|-------------|
| **Main Layout** | `*Layout.vue` | Navbar, sidebar, page shell — wraps all routes |
| **Home Page** | `*Home.vue` | Custom dashboard (hero banners, recently added rows) |
| **Library Views** | `*Library.vue` | Custom game grid/list for GOG, Games, Emulation |
| **Search** | `*Search.vue` | Global search results page |
| **Couch Mode** | `*Couch.vue` | Full-screen controller UI for TV (platform carousel, game browser, video playback) |
| **CSS Overrides** | `neon-horizon.css` | Style overrides for existing GD components |
| **JS Effects** | `neon-horizon.js` | Dynamic effects (gradient text, glass blur, glow) |
| **Static Assets** | `assets/` | Images, icons, logos, metadata JSON — served via `/api/plugins/{id}/assets/` |

### How theme compilation works

1. Plugin provides `.vue` files + `plugin.json` with `"type": "theme"`
2. On container startup, GD's entrypoint runs `compile-theme-plugins.mjs`
3. Vite compiles all `.vue` files into a single IIFE bundle (`layout.js` + `layout.css`)
4. Frontend loads the bundle and registers the layout/couch components
5. When user selects your theme in Settings > Appearance, your components render

### Vue files — important rules

Plugin Vue files are compiled **outside the main app bundle**. They cannot import from `@/` paths. Instead, use:

```typescript
// Access Vue runtime
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// Access GD stores, API, and utilities via window.__GD__
const _gd = (window as any).__GD__
const client = _gd.api                          // Axios client with auth
const auth = _gd.stores.auth()                   // User info (token hidden for security)
const themeStore = _gd.stores.theme()            // Theme settings
const socketStore = _gd.stores.socket()          // WebSocket (sync progress hidden)

// Composables for Couch Mode
const { useCouchNav, couchNavPaused } = _gd.composables
const getEjsCore = _gd.getEjsCore               // Platform → EmulatorJS core mapping

// Register your components
_gd.registerPluginLayout('my-theme', LayoutComponent)
_gd.registerPluginCouchMode('my-theme', CouchComponent)
_gd.registerTheme({ id: 'my-theme', name: 'My Theme', ... })
```

**Global components** available in plugin templates (registered in GD's `main.ts`):
- `<DownloadManager />` — Download queue tray (admin only)
- `<RandomGamePicker />` — Random game dice button
- `<AmbientBackground />` — Animated orb background (respects theme settings)

### Plugin assets

Theme plugins can bundle static assets in an `assets/` directory. These are served via:
```
/api/plugins/{plugin-id}/assets/{path}
```

Example: `/api/plugins/neon-horizon/assets/pop/snes.webp`

Use the helper in your Vue component:
```typescript
const PLUGIN_ID = 'my-theme'
function pluginAsset(path: string): string {
  return `/api/plugins/${PLUGIN_ID}/assets/${path}`
}
```

### Theme definition (plugin.py)

```python
from plugins.hookspecs import hookimpl

class Plugin:
    @hookimpl
    def frontend_get_theme(self):
        return {
            "id": "my-theme",
            "name": "My Theme",
            "description": "A custom theme",
            "layout": "my-theme",         # must match registerPluginLayout() id
            "skins": [
                {"id": "blue", "name": "Ocean Blue", "preview": "#2563eb"},
                {"id": "red",  "name": "Crimson",    "preview": "#dc2626"},
            ],
            "defaultSkin": "blue",
            "cssFile": "my-theme",
            "font": "https://fonts.googleapis.com/css2?family=MyFont&display=swap",
            "previewHtml": "<div>...</div>",  # optional: custom preview in theme switcher
            "settings": [
                {
                    "key": "glassBlur",
                    "label": "Glass Blur",
                    "type": "range",
                    "default": 20,
                    "min": 0, "max": 60, "step": 1,
                    "unit": "px",
                    "cssVar": "--my-glass-blur",
                },
            ],
        }

    @hookimpl
    def frontend_get_css(self):
        return Path(__file__).parent.joinpath("my-theme.css").read_text()

    @hookimpl
    def frontend_get_js(self):
        return Path(__file__).parent.joinpath("my-theme.js").read_text()
```

### Theme settings

Settings defined in `frontend_get_theme()` → `settings` array are:
- Rendered automatically in Settings > Appearance > Theme Settings
- Applied as CSS custom properties on `:root` via the theme store
- Readable in plugin JS via `getComputedStyle(root).getPropertyValue('--my-var')`

**Note:** Pinia store reactivity may not work reliably in compiled plugin components. Poll CSS variables instead:
```typescript
setInterval(() => {
  const cs = getComputedStyle(document.documentElement)
  myValue.value = cs.getPropertyValue('--my-css-var').trim()
}, 1500)
```

---

## Plugin manifest (plugin.json)

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "What this plugin does",
  "type": "theme",
  "entry": "plugin.py",
  "has_logo": true,
  "min_gd_version": "3.0.0",
  "config_schema": {}
}
```

### Required fields

| Field | Description |
|-------|-------------|
| `id` | Unique identifier, lowercase with dashes (e.g. `my-theme`) |
| `name` | Display name shown in Settings |
| `version` | Semantic version (e.g. `1.0.0`) |
| `author` | Your name or handle |
| `type` | One of: `metadata`, `download`, `library`, `theme`, `widget`, `lifecycle` |
| `entry` | Python file containing the `Plugin` class (usually `plugin.py`) |

### Optional fields

| Field | Description |
|-------|-------------|
| `description` | Short description shown in Settings |
| `has_logo` | Set to `true` if plugin has `logo.png` or `logo.svg` |
| `requires` | List of pip package names needed by the plugin |
| `min_gd_version` | Minimum GamesDownloader version required |
| `config_schema` | Configuration fields (rendered as form in Settings > Plugins) |

## Plugin class

Your `plugin.py` must define a `Plugin` class that implements hooks:

```python
from plugins.hookspecs import hookimpl

class Plugin:
    @hookimpl
    def metadata_provider_name(self) -> str:
        return "My Source"
```

## Available hooks

See [docs/HOOKS.md](docs/HOOKS.md) for the full hook reference.

## Installing plugins

1. Go to **Settings > Plugins** in GamesDownloader
2. Drag and drop your `.zip` file into the install area
3. The plugin is extracted, dependencies installed, and loaded automatically
4. Enable/disable and configure from the same page
5. **For theme plugins with `.vue` files:** restart the container after install (Vite compiles them on startup)

---

## Examples

### NEON HORIZON Theme (`examples/neon-horizon/`)

A complete theme plugin inspired by [Colorful Pop](https://github.com/RobZombie9043/colorful-pop-es-de) for EmulationStation, adapted for web with neon cyberpunk aesthetics.

**Main Layout:**
- Netflix-style home page with hero banner and recently added rows
- Library tabs in navbar (GOG, Games, Emulation)
- Steam Big Picture style library views (16:9 landscape cards)
- Global search across all libraries
- Alphabet quick-nav sidebar

**Couch Mode (Colorful Pop style):**
- Platform carousel with pop character artwork
- Overlay console setups with real game video playing inside TV cutouts (video positions computed from EmulationStation XML)
- Pop → overlay+video → pop automatic cycling
- Game list (text list + big screenshot) and carousel (full-screen fanart) views
- Platform descriptions in 15 languages (auto-detected from browser)
- Per-platform system colors from EmulationStation metadata
- Wheel logo display during video playback
- Visual settings: Ken Burns animation, video cycle, video volume, icon animations

**Theme Features:**
- 8 color skins (Cyan Flux, Violet Surge, Magenta Pulse, Gold Circuit, Cyber, Plasma, Sunset, Aurora)
- Typography: Orbitron headers, Rajdhani body
- Ambient orbs, floating particles, grid overlay, scanline CRT effect
- Glass morphism with configurable blur and opacity
- Settings integration: all visual effects controllable from Settings > Appearance

**Plugin type:** `theme` (implements `FrontendProviderSpec`)

**Files:**
```
examples/neon-horizon/
  NeonHorizonLayout.vue    # Main shell (navbar, particles, route detection)
  NeonHorizonHome.vue      # Home page (hero banner, recently added)
  NeonHorizonLibrary.vue   # Library view (Big Picture cards, alphabet)
  NeonHorizonSearch.vue    # Global search results
  NeonHorizonCouch.vue     # Couch Mode (Colorful Pop style)
  neon-horizon.css         # CSS overrides for existing GD components
  neon-horizon.js          # Dynamic effects (gradient text, glass blur)
  plugin.py                # Theme definition, skins, settings
  plugin.json              # Manifest
  logo.svg                 # Plugin icon (retrowave sun)
  assets/                  # Static assets (served via /api/plugins/neon-horizon/assets/)
    pop/                   # Pop character artwork per platform (95 platforms)
    overlay/               # Console overlay with TV cutout (RGBA transparency)
    artwork/               # Modern console artwork (Ken Burns background)
    icons/                 # Colored platform icons
    logos/                 # SVG platform name logos
    platforms.json         # Platform metadata (names, colors, descriptions, 15 languages)
    videopos.json          # Video positions inside TV cutouts (computed from ES-DE XML)
```

### PPE.pl Metadata Scraper (`examples/ppe-metadata/`)

A metadata plugin that scrapes game data from PPE.pl (Polish gaming website).

**Plugin type:** `metadata`

### Description Translator (`examples/gd3-translator/`)

Translates game descriptions between 26 languages using Google Translate.

**Plugin type:** `lifecycle`

---

## Directory structure

```
gd3-plugin-template/
  templates/
    metadata-scraper/   # starter template for metadata plugins
    theme/              # starter template for theme plugins (plugin.py, CSS, JS, JSON)
    widget/             # starter template for widget plugins
  examples/
    neon-horizon/       # complete theme (Vue layouts, couch mode, CSS, JS, 95 platform assets)
    ppe-metadata/       # complete metadata scraper (PPE.pl)
    gd3-translator/     # complete translator (26 languages)
  docs/
    HOOKS.md            # detailed hook reference (all specs, window.__GD__ API, Vue compilation)
  build.sh              # ZIP packaging helper
```

---

## Credits & Acknowledgments

NEON HORIZON theme's Couch Mode is inspired by and uses assets from EmulationStation themes by [RobZombie9043](https://github.com/RobZombie9043):

- **[Colorful Pop](https://github.com/RobZombie9043/colorful-pop-es-de)** — Platform artwork (pop, overlay, modern), SVG logos, colored icons, platform metadata with 15-language descriptions, video positioning data, and system color palettes
- **[Elementerial](https://github.com/RobZombie9043/elementerial-es-de)** — Additional design inspiration

These EmulationStation themes are licensed under **Creative Commons CC-BY-NC-SA**. The assets are included in the NEON HORIZON plugin for non-commercial, personal use in accordance with this license. All credit for the original artwork and metadata goes to RobZombie9043.

## License

MIT (plugin template code). Theme assets may have separate licenses — see credits above.
