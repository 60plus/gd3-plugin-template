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
    "id": "my-theme",                    # unique, matches compiled layout ID
    "name": "My Theme",                  # display name in Settings > Appearance
    "description": "Short description",
    "layout": "my-theme",                # layout ID - maps to MyThemeLayout.vue / MyThemeCouch.vue
    "skins": [                           # color palettes user can choose
        {"id": "blue",  "name": "Ocean",  "preview": "#2563eb"},
        {"id": "red",   "name": "Crimson","preview": "#dc2626"},
        # dual-color gradient skins:
        {"id": "sunset","name": "Sunset", "preview": "linear-gradient(135deg,#f97316,#ec4899)", "dual": True},
    ],
    "defaultSkin": "blue",
    "cssFile": "my-theme",               # base name of CSS file (loaded by theme store)
    "font": "https://fonts.googleapis.com/css2?family=MyFont&display=swap",  # optional Google Fonts URL
    "previewHtml": "<div style='...'>...</div>",  # optional: custom preview card in theme switcher
    "settings": [                        # optional: per-theme settings in Settings > Appearance
        {
            "key": "glassBlur",
            "label": "Glass Blur",       # can be an i18n key (e.g. "nh.setting_blur")
            "hint": "Backdrop blur strength",
            "type": "range",             # range | toggle | select
            "default": 20,
            "min": 0, "max": 60, "step": 1,
            "unit": "px",                # appended to value when setting CSS var (see below)
            "cssVar": "--my-glass-blur",  # set on :root by theme store
        },
        {
            "key": "particles",
            "label": "Particle Count",
            "type": "select",
            "default": "6",
            "options": ["0", "3", "6", "12"],
            "optionLabels": ["None", "Few", "Normal", "Many"],  # can be i18n keys (see below)
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

#### font field

The `font` field is optional. When provided, it should be a Google Fonts CSS URL. The app loads it as a `<link>` tag in `<head>`, making the font family available for use in your CSS:

```css
[data-theme="my-theme"] {
  font-family: 'MyFont', sans-serif;
}
```

#### CSS variable unit field

Range settings support an optional `"unit"` string (e.g. `"px"`, `"deg"`, `"%"`, `"em"`). When the theme store sets the CSS variable on `:root`, it appends the unit to the numeric value:

| Value | Unit | CSS Variable Result |
|-------|------|---------------------|
| `30` | `"px"` | `--my-glass-blur: 30px` |
| `45` | `"deg"` | `--my-angle: 45deg` |
| `80` | `"%"` | `--my-opacity: 80%` |
| `1.5` | `"em"` | `--my-spacing: 1.5em` |
| `6` | (none) | `--my-count: 6` |

If `unit` is omitted, the raw numeric value is used.

#### optionLabels with i18n

The `optionLabels` array can contain either plain text strings or i18n keys. When an option label matches an i18n key, the Settings UI translates it automatically:

```python
# Plain text (not translated)
"optionLabels": ["None", "Few", "Normal", "Many"],

# i18n keys (translated via plugin's i18n.json)
"optionLabels": ["nh.opt_none", "nh.opt_few", "nh.opt_normal", "nh.opt_many"],
```

The same applies to `label` and `hint` fields - they can be i18n keys from your plugin's `i18n.json`.

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

### data-theme and data-skin attributes

When a theme is activated, the app sets two attributes on the `<html>` element:

- `data-theme` - set to the theme's `id` (e.g. `data-theme="neon-horizon"`)
- `data-skin` - set to the selected skin's `id` (e.g. `data-skin="nh-cyber"`)

These attributes allow you to scope CSS to your theme so styles don't leak into other themes:

```css
/* Only applies when your theme is active */
[data-theme="my-theme"] {
  --bg-primary: #0a0a1a;
  --text-color: #e2e8f0;
}

/* Skin-specific overrides */
[data-theme="my-theme"][data-skin="sunset"] {
  --pl: #f97316;
}

/* Skin-only selector also works */
[data-skin="nh-cyber"] {
  --pl: #00d4ff;
}
```

### Theme settings - CSS variable flow

1. Plugin defines `settings` with `cssVar` in `frontend_get_theme()`
2. User changes setting in Settings > Appearance > Theme Settings
3. Theme store calls `applyToDOM()` - sets CSS variable on `:root` inline style
4. Theme store dispatches `CustomEvent('gd-theme-updated')` on `<html>`
5. Plugin JS/Vue reads the CSS variable and applies effects

### gd-theme-updated event

The `gd-theme-updated` custom event is dispatched on the `<html>` element whenever any theme setting changes (slider moved, toggle flipped, skin switched, etc.). Plugins can listen to this event to react to setting changes in JavaScript:

```javascript
document.documentElement.addEventListener('gd-theme-updated', () => {
  // Re-read CSS variables and update your effects
  const blur = getComputedStyle(document.documentElement)
    .getPropertyValue('--my-glass-blur').trim();
  applyBlurEffect(blur);
});
```

This is the recommended approach for compiled Vue plugins, since Pinia store reactivity may not work across the plugin boundary.

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
3. Finds `.vue` files - `*Layout.vue` = main layout, `*Couch.vue` = couch mode
4. Compiles via Vite into IIFE bundle - `/app/static/plugin-layouts/{id}/layout.js` + `layout.css`
5. Frontend loads bundle from manifest - auto-registers layout and couch components

Compiled plugins auto-register - you do not need to call `registerPluginLayout()` or `registerPluginCouchMode()` manually. The compiler generates the registration code as part of the IIFE bundle.

**Externalized dependencies** (not bundled, provided by GD at runtime):
- `vue` - `window.__GD__.Vue`
- `vue-router` - `window.__GD__.VueRouter`

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

    // Theme/layout registration (only needed for non-Vue JS plugins)
    registerTheme(themeDefinition),
    registerPluginLayout(layoutId, VueComponent),
    registerPluginCouchMode(themeId, VueComponent),

    // Couch Mode composables
    composables: {
        useCouchNav(handlers),    // gamepad + keyboard navigation (see below)
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

### useCouchNav handlers

The `useCouchNav(handlers)` composable connects gamepad and keyboard input to your couch mode UI. The `handlers` parameter is an object with callback functions for each direction/action:

```typescript
const { useCouchNav, couchNavPaused } = _gd.composables

useCouchNav({
  left:    () => { /* D-pad left / Arrow Left  - navigate left */ },
  right:   () => { /* D-pad right / Arrow Right - navigate right */ },
  up:      () => { /* D-pad up / Arrow Up       - navigate up */ },
  down:    () => { /* D-pad down / Arrow Down   - navigate down */ },
  confirm: () => { /* A button / Enter          - select/confirm */ },
  back:    () => { /* B button / Escape         - go back */ },
  menu:    () => { /* Start button / M key      - open menu */ },
})
```

All handlers are optional - only provide the ones you need. Input is automatically paused when `couchNavPaused.value` is `true` (e.g. during modal overlays or emulator sessions).

### Plugin asset serving

Static files in `assets/` subdirectory are served via:
```
GET /api/plugins/{plugin-id}/assets/{file-path}
```

Supported types: `.webp`, `.png`, `.jpg`, `.svg`, `.xml`, `.json`

Path traversal protection: `..` and absolute paths are blocked.

JSON files can be loaded via the API client for data-driven plugins:
```typescript
const { data } = await client.get('/api/plugins/my-plugin/assets/data.json')
```

### Plugin i18n endpoint

```
GET /api/plugins/frontend/i18n
```

Returns merged translations from all installed plugins' `i18n.json` files. The response format:

```json
{
  "en": {
    "nh.setting_particles": "Particle Count",
    "nh.opt_none": "None",
    "retro.title": "Retro Wave"
  },
  "pl": {
    "nh.setting_particles": "Liczba czastek",
    "nh.opt_none": "Brak",
    "retro.title": "Retro Wave"
  }
}
```

This endpoint is called automatically on app startup. The returned translations are merged into the app's i18n system via `_gd.i18n.merge()`. Plugin developers do not need to call this endpoint manually - just provide an `i18n.json` file in your plugin root directory.

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
