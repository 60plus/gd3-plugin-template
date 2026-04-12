# Hook Reference

All hooks are defined in `plugins/hookspecs.py`. Use `@hookimpl` decorator from `plugins.hookspecs` to implement them.

```python
from plugins.hookspecs import hookimpl

class Plugin:
    @hookimpl
    def hook_name(self, ...):
        ...
```

---

## FrontendProviderSpec (Theme Plugins)

For plugins that provide themes, custom layouts, CSS, JavaScript, and routes.

| Hook | Returns | Description |
|------|---------|-------------|
| `frontend_get_theme()` | `dict or None` | Theme definition (layout, skins, settings) |
| `frontend_get_css()` | `str or None` | CSS string injected into `<head>` via `/api/plugins/frontend/css` |
| `frontend_get_js()` | `str or None` | JavaScript string injected into `<head>` via `/api/plugins/frontend/js` |
| `frontend_get_routes()` | `list[dict] or None` | Custom page routes (reserved for future use) |

### Theme definition dict

Returned by `frontend_get_theme()`:

```python
{
    "id": "my-theme",                    # unique, matches registerPluginLayout() call
    "name": "My Theme",                  # display name in Settings > Appearance
    "description": "Short description",
    "layout": "my-theme",                # layout ID - must match plugin's registerPluginLayout()
    "skins": [                           # color palettes user can choose
        {"id": "blue",  "name": "Ocean",  "preview": "#2563eb"},
        {"id": "red",   "name": "Crimson","preview": "#dc2626"},
        # dual-color gradient skins:
        {"id": "sunset","name": "Sunset", "preview": "linear-gradient(135deg,#f97316,#ec4899)", "dual": True},
    ],
    "defaultSkin": "blue",
    "cssFile": "my-theme",               # base name of CSS file (loaded by theme store)
    "font": "https://fonts.googleapis.com/css2?family=MyFont&display=swap",  # optional
    "previewHtml": "<div style='...'>...</div>",  # optional: custom preview card in theme switcher
    "settings": [                        # optional: per-theme settings in Settings > Appearance
        {
            "key": "glassBlur",
            "label": "Glass Blur",
            "hint": "Backdrop blur strength",
            "type": "range",             # range | toggle | select
            "default": 20,
            "min": 0, "max": 60, "step": 1,
            "unit": "px",                # appended to value when setting CSS var
            "cssVar": "--my-glass-blur",  # set on :root by theme store
        },
        {
            "key": "particles",
            "label": "Particle Count",
            "type": "select",
            "default": "6",
            "options": ["0", "3", "6", "12"],
            "optionLabels": ["None", "Few", "Normal", "Many"],
            "cssVar": "--my-particle-count",
        },
        {
            "key": "scanlines",
            "label": "Scanline Overlay",
            "type": "toggle",
            "default": False,
            "cssVar": "--my-scanlines",   # set to "1" or "0"
        },
    ],
}
```

### Skin definition

```python
{
    "id": "blue",                # unique within theme
    "name": "Ocean Blue",        # display name
    "preview": "#2563eb",        # hex color OR CSS gradient for UI swatch
    "dual": False,               # True for dual-color gradient skins (shown in second row)
}
```

Skins are rendered as colored circles in Settings > Appearance. The selected skin sets `data-skin` attribute on `<html>`, and your CSS uses `[data-skin="blue"]` to apply colors.

### Theme settings - CSS variable flow

1. Plugin defines `settings` with `cssVar` in `frontend_get_theme()`
2. User changes setting in Settings > Appearance > Theme Settings
3. Theme store calls `applyToDOM()` → sets CSS variable on `:root` inline style
4. Theme store dispatches `CustomEvent('gd-theme-updated')` on `<html>`
5. Plugin JS/Vue reads the CSS variable and applies effects

**Important for compiled Vue plugins:** Pinia store reactivity may not work across the plugin boundary. Poll CSS variables instead:
```javascript
const cs = getComputedStyle(document.documentElement)
const val = cs.getPropertyValue('--my-css-var').trim()
```

### previewHtml security

`previewHtml` is sanitized with DOMPurify before rendering. Only `<div>` and `<span>` tags with `style` attribute are allowed. No scripts, images, links, or event handlers.

### Vue SFC compilation

Theme plugins with `.vue` files are compiled on container startup:

1. `entrypoint.sh` runs `compile-theme-plugins.mjs`
2. Script scans `/data/plugins/` for `plugin.json` with `"type": "theme"`
3. Finds `.vue` files → `*Layout.vue` = main layout, `*Couch.vue` = couch mode
4. Compiles via Vite into IIFE bundle → `/app/static/plugin-layouts/{id}/layout.js` + `layout.css`
5. Frontend loads bundle from manifest → calls `registerPluginLayout()` and `registerPluginCouchMode()`

**Externalized dependencies** (not bundled, provided by GD at runtime):
- `vue` → `window.__GD__.Vue`
- `vue-router` → `window.__GD__.VueRouter`

### window.__GD__ API reference

Available to all plugin JavaScript (both `frontend_get_js()` and compiled Vue components):

```javascript
window.__GD__ = {
    // Vue runtime (all exports from 'vue')
    Vue: { ref, computed, watch, onMounted, onUnmounted, nextTick, defineComponent, ... },

    // Vue Router (all exports from 'vue-router')
    VueRouter: { useRouter, useRoute, RouterLink, RouterView, ... },

    // Pinia stores (factory functions - call to get instance)
    stores: {
        auth(),     // returns { user, logout() } - token BLOCKED for security
        socket(),   // returns { syncProgress } - raw socket BLOCKED
        theme(),    // returns full theme store (themeId, skinId, settings, applyToDOM, ...)
    },

    // Authenticated Axios client (Bearer token auto-attached)
    api: AxiosInstance,

    // Theme/layout registration
    registerTheme(themeDefinition),
    registerPluginLayout(layoutId, VueComponent),
    registerPluginCouchMode(themeId, VueComponent),

    // Couch Mode composables
    composables: {
        useCouchNav(handlers),    // gamepad + keyboard navigation
        couchNavPaused,           // ref<boolean> - pause input during overlays
        useCouchTheme(),          // { theme, view, setTheme, setView }
    },

    // EmulatorJS core mapping
    getEjsCore(platformFsSlug),   // returns core name or null

    // i18n - translation system
    i18n: {
        t(key, params?),          // translate key, fallback to key string
        locale,                   // readonly ref<string> current locale
        setLocale(code),          // change locale
        merge(translations),      // merge plugin translations { "en": {...}, "pl": {...} }
    },

    // Notification system - badge on user avatar
    notifications: {
        add({ id, count, label, details?, action?, actionLabel? }),  // add/update notification
        dismiss(id),              // hide until session restart
        remove(id),               // remove permanently
        store,                    // reactive Pinia store (items, active, totalCount, hasBadge)
    },
}
```

### Plugin asset serving

Static files in `assets/` subdirectory are served via:
```
GET /api/plugins/{plugin-id}/assets/{file-path}
```

Supported types: `.webp`, `.png`, `.jpg`, `.svg`, `.xml`, `.json`

Path traversal protection: `..` and absolute paths are blocked.

---

## MetadataProviderSpec

For plugins that fetch game metadata from external sources.

| Hook | Returns | Description |
|------|---------|-------------|
| `metadata_provider_name()` | `str` | Display name (e.g. "PPE.pl") |
| `metadata_provider_id()` | `str` | Unique ID (e.g. "ppe") |
| `metadata_search_game(query)` | `list[dict]` | Search results |
| `metadata_get_game(provider_game_id)` | `dict or None` | Full game metadata |
| `metadata_get_cover_url(provider_game_id)` | `str or None` | Cover image URL |

### Search result dict

```python
{
    "provider_id": "ppe",
    "provider_game_id": "https://www.ppe.pl/gry/Game/123",
    "name": "Game Title",
    "snippet": "Short description",
}
```

### Game metadata dict

```python
{
    "provider_id": "ppe",
    "provider_game_id": "https://www.ppe.pl/gry/Game/123",
    "title": "Game Title",
    "description": "Full description text",
    "rating": 8.5,
    "genre": "FPS",
    "release_date": "2024-01-15",
    "developer": "Studio Name",
    "screenshots": ["https://example.com/screen1.jpg", ...],
    "source_url": "https://www.ppe.pl/gry/Game/123",
}
```

---

## DownloadProviderSpec

For plugins that handle game downloads.

| Hook | Returns | Description |
|------|---------|-------------|
| `download_provider_name()` | `str` | Display name |
| `download_provider_id()` | `str` | Unique ID |
| `download_can_handle(game_id)` | `bool` | Can this provider download this game? |
| `download_start(game_id, destination)` | `dict` | Start download, return `{task_id}` |
| `download_get_status(task_id)` | `dict` | Progress: `{progress, status, ...}` |

---

## LibrarySourceSpec

For plugins that scan game libraries from various sources.

| Hook | Returns | Description |
|------|---------|-------------|
| `library_source_name()` | `str` | Display name |
| `library_source_id()` | `str` | Unique ID |
| `library_scan(path)` | `list[dict]` | Discovered games/ROMs |

---

## LifecycleSpec

For plugins that react to application events.

| Hook | Returns | Description |
|------|---------|-------------|
| `lifecycle_on_game_added(game)` | `None` | Called when a game is added |
| `lifecycle_on_download_complete(game, path)` | `None` | Called when a download finishes |
| `lifecycle_on_startup()` | `None` | Called on app start |
| `lifecycle_on_shutdown()` | `None` | Called on app stop |

---

## WidgetSpec

For plugins that add dashboard cards.

| Hook | Returns | Description |
|------|---------|-------------|
| `widget_get_cards()` | `list[dict] or None` | Widget card definitions |
