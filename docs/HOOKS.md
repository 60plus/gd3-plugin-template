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
        auth(),       // returns { user, logout() } - token BLOCKED for security
        socket(),     // returns { syncProgress } - raw socket BLOCKED
        theme(),      // returns full theme store (themeId, skinId, settings, applyToDOM, ...)
        libraries(),  // library registry store - see "Library Registry API" below (v1.0.11)
        collections(),// collections registry store - see "Collections API" below (v1.0.12)
    },

    // Authenticated Axios client (Bearer token auto-attached)
    api: AxiosInstance,

    // Shared utility helpers for theme/plugin authors (v1.0.12) - see "Shared utilities" below
    utils: {
        buildLanguageList(dict),  // [{ name, flag }] from a languages object
        sanitizeHtml(html),       // sanitize an HTML description for v-html
    },

    // Theme/layout registration (only needed for non-Vue JS plugins)
    registerTheme(themeDefinition),
    registerPluginLayout(layoutId, VueComponent),
    registerPluginCouchMode(themeId, VueComponent),
    registerMetadataTab(tab),     // add a tab to the game metadata editor (see below)
    registerDetailRow(row),       // add a theme-native row to the game detail card (v1.0.10)

    // Library registry helpers (v1.0.11) - see "Library Registry API" below
    recentLibraries: {
        get(),            // resolved slugs to show a recently-added row for (visible, non-couch)
        getRaw(),         // raw per-theme selection (null = all)
        isEnabled(slug),  // should this library show a recently-added row?
        set(slugs),       // persist the per-theme selection
    },
    icons: {
        library(name),    // inner SVG markup for a built-in library icon (tint with currentColor)
        libraryNames(),   // list of built-in icon names
        libraryAll(),     // { name: svgMarkup } map
    },

    // Collections - admin-curated game groupings (v1.0.12) - see "Collections API" below
    collections: {
        list(),              // reactive array of collections
        fetch(),             // (re)load the collections list
        bySlug(slug),        // a loaded collection summary by slug
        get(slug),           // full detail incl. member games (Promise)
        forGame(id),         // slugs of the collections a game belongs to (Promise)
        route(slug),         // route to one collection (nested under its container library)
        libraryRoute(lib),   // route to a container library's collection grid
    },

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

### Library Registry API (`stores.libraries`) - v1.0.11

Libraries (GOG, Games, Emulation, Couch, and admin-created custom libraries) are
data-driven from a registry. A theme should render its navigation, home rows and
library views from this store instead of hard-coding GOG / Games / Emulation - so
that custom libraries, per-user visibility, ordering and access control all work
automatically, with no further changes to GamesDownloader.

```javascript
const libs = window.__GD__.stores.libraries();
```

| Member | Type | Description |
|--------|------|-------------|
| `visible` | `LibraryInfo[]` | Libraries this user should see - already filtered (enabled, not hidden, RBAC + per-user access) and sorted in the user's effective order. **Iterate this for nav / home.** |
| `enabled` | `LibraryInfo[]` | Like `visible`, but ignores the per-user hide (the admin-enabled set). |
| `bySlug(slug)` | `LibraryInfo \| undefined` | Look up one library. |
| `has(slug)` | `boolean` | Library exists, is enabled and visible to this user. |
| `isHidden(slug)` | `boolean` | The user hid this library from their own view. |
| `orderIndex(slug)` | `number` | Effective per-user sort position - use as a CSS `order` value. |
| `route(lib)` | `string` | Frontend list-route path (built-ins → `/library` / `/games` / `/emulation` / `/couch`; custom → `/lib/:slug`). |
| `label(lib)` | `string` | Localised display name (built-ins use the UI translations; custom = its name). |
| `slugForPath(path)` | `string \| null` | Which library a list-route path belongs to (`null` = not a library list route, e.g. a detail page). Decide which library view to render and which library to fetch. |
| `loaded` | `boolean` | The registry has been fetched. |
| `fetch()` | `Promise` | (Re)load the registry. |

`route`, `label` and `slugForPath` accept either a slug string or a `LibraryInfo`.

**`LibraryInfo`:**
```typescript
{ slug, name, kind, icon, color, enabled, sort_order, is_builtin, storage_folder }
// kind: "gog" | "custom" | "custom_lib" | "emulation" | "couch" | "collections"
// icon: "builtin:<name>" | "/resources/..." (uploaded image) | null
```

#### Recently-added rows - `window.__GD__.recentLibraries`

Per-theme, per-user choice of which libraries show a "recently added" row on the
home page. Drive your home feed from it:

```javascript
const recent = window.__GD__.recentLibraries;
recent.isEnabled('games');   // show a recently-added row for this library?
recent.get();                // resolved list of slugs to show (visible, non-couch)
```

#### Library icons - `window.__GD__.icons`

A library's `icon` is either an uploaded image URL or a `"builtin:<name>"` token.
For built-ins, fetch the inline SVG markup and tint it with the library colour:

```javascript
const lib = libs.bySlug('games');
if (lib.icon && lib.icon.startsWith('builtin:')) {
  const svg = window.__GD__.icons.library(lib.icon.slice(8)); // inner <path…> markup
  el.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="${lib.color}" stroke-width="2">${svg}</svg>`;
} else if (lib.icon) {
  el.innerHTML = `<img src="${lib.icon}">`;
}
```

#### Example - a data-driven nav

```javascript
const libs = window.__GD__.stores.libraries();
const { useRouter } = window.__GD__.VueRouter;
const router = useRouter();

// Tabs in the user's order (couch usually has its own entry / view)
const tabs = [...libs.visible]
  .filter(l => l.kind !== 'couch')
  .sort((a, b) => libs.orderIndex(a.slug) - libs.orderIndex(b.slug))
  .map(l => ({ label: libs.label(l), to: libs.route(l), order: libs.orderIndex(l.slug) }));

// Which of MY library views to render for the current route (null on detail pages):
const slug = libs.slugForPath(router.currentRoute.value.path);
```

#### Reactivity (compiled Vue themes)

As with theme settings, Pinia reactivity may not cross the plugin boundary.
Snapshot what you render into a local `ref` and refresh it on the
`gd-theme-updated` event (fired on hide / reorder / recently-added changes) plus a
light poll - see the **gd-theme-updated event** section above.

### Collections API (`stores.collections` / `__GD__.collections`) - v1.0.12

Collections are admin-curated groupings of related games (for example a series or a
franchise), styled like the rest of the library. Each collection lives inside a
**container library** (a library of `kind: "collections"`), so a theme can render
the collection grid and the per-collection detail page entirely data-driven, the
same way it renders libraries.

The container library already appears in `stores.libraries().visible` (its `kind`
is `"collections"`), so your existing nav / library code lists it automatically.
Use this API to fill in the grid of collections and the collection detail.

```javascript
const collections = window.__GD__.collections;
```

| Member | Type | Description |
|--------|------|-------------|
| `list()` | `CollectionInfo[]` | Reactive list of all collections (read after boot, or call `fetch()` first). |
| `fetch()` | `Promise` | (Re)load the collections list. |
| `bySlug(slug)` | `CollectionInfo \| undefined` | A loaded collection summary by slug. |
| `get(slug)` | `Promise<CollectionDetail>` | A collection's full detail, including its member games. |
| `forGame(id)` | `Promise<string[]>` | The collection slugs a game belongs to. |
| `route(slug)` | `string` | Route to one collection, nested under its container library (`/collections/:lib/:slug`). |
| `libraryRoute(lib)` | `string` | Route to a container library's collection grid (`/collections/:lib`). |

The same helpers are also exposed as a raw Pinia store at
`window.__GD__.stores.collections()`.

**`CollectionInfo`** (summary, from `list` / `bySlug`):
```typescript
{
  slug, name, library,             // library = slug of the container library
  description, description_short,  // long (About) + short (list hero) - may contain HTML
  cover_path,                      // custom cover, or null = auto fan of member covers
  member_covers, member_heroes,    // arrays of member art URLs (fan covers / backdrops)
  member_count,
  start_year, end_year, rating,    // aggregated from members unless overridden
  developers, publishers, sources, platforms,  // aggregated from member games
}
```

**`CollectionDetail`** (from `get(slug)`) adds the resolved member games plus the
aggregated metadata used by the detail view:
```typescript
{
  ...CollectionInfo,
  games: GameDict[],               // member games (id, title, cover, source, gog_game_id, ...)
  genres: string[],
  languages: { [code]: ... },      // merged languages dict (same shape as a game) - feed buildLanguageList
  hltb_main_s, hltb_complete_s,    // average (or overridden) time-to-beat, in seconds
}
```

> **Opening a member game:** a member game with `source === 'gog'` must be opened by
> its `gog_game_id` (the GOG detail route resolves by GOG id); every other game by
> its `id`. Mixing the two opens the wrong game.

#### Example - a collection grid

```javascript
const collections = window.__GD__.collections;

await collections.fetch();
const cards = collections.list()
  .filter(c => c.library === containerSlug)        // collections in this container
  .map(c => ({ name: c.name, to: collections.route(c.slug), covers: c.member_covers }));
```

#### Reactivity

As with the library registry, Pinia reactivity may not cross the plugin boundary -
snapshot what you render into a local `ref` and refresh it on the
`gd-theme-updated` event plus a light poll (see the **gd-theme-updated event**
section above).

### Shared utilities - `window.__GD__.utils` (v1.0.12)

Helpers the built-in themes use, exposed so plugins produce identical output
without importing app internals (plugins only have `window.__GD__`, not `@/utils`).

```javascript
const { buildLanguageList, sanitizeHtml } = window.__GD__.utils || {};
```

| Helper | Signature | Description |
|--------|-----------|-------------|
| `buildLanguageList(dict)` | `(languages) => { name, flag }[]` | Turns a game's (or collection's) languages object into the display list the built-in themes use. `flag` is a `flag-icons` ISO-2 code - render it as `<span class="fi fi-${flag}">`. |
| `sanitizeHtml(html)` | `(html) => string` | Sanitizes an HTML string (a game / collection description) for safe use with `v-html` or `innerHTML`. |

Guard for older cores, since `utils` is only present on v1.0.12+:
```javascript
const _u = window.__GD__.utils || {};
const sanitizeHtml = _u.sanitizeHtml || (h => h);
const buildLanguageList = _u.buildLanguageList || (() => []);
```

### registerMetadataTab

Adds a tab to the **Edit Metadata** panel of a library game, next to the
built-in Cover / Description / Details tabs. The tab body is mounted as plain
DOM, so it works from a `frontend_get_js()` plugin without compiling a Vue
component (a metadata plugin can use it too - hooks are not gated by plugin
`type`). Available since GamesDownloader **v1.0.3** - guard the call so your
plugin degrades gracefully on older versions (the rest of your plugin keeps
working, only the tab is skipped).

```javascript
const gd = window.__GD__;
if (gd && typeof gd.registerMetadataTab === 'function') {
  gd.registerMetadataTab({
    id: 'my-tab',            // unique tab id
    label: 'My Source',      // tab button label
    library: 'games',        // 'games' | 'gog' | 'all'  (default 'games')
    mount(el, ctx) {
      // el  - empty container element for your tab body
      // ctx - { game, apiPrefix, close, save }
      el.textContent = 'Editing ' + ctx.game.title;
      // build your UI, then persist via the authenticated client:
      //   gd.api.patch(ctx.apiPrefix + '/' + ctx.game.id, { meta_ratings: {...} })
      //     .then(() => ctx.save());
      return () => { /* optional cleanup, called when the tab is left */ };
    },
  });
}
```

`mount(el, ctx)` receives a context object:

| Field | Description |
|-------|-------------|
| `game` | The game record being edited (`id`, `title`, `meta_ratings`, ...) |
| `apiPrefix` | API base for this panel, e.g. `/library/games` or `/gog/library/games` |
| `close()` | Close the metadata panel |
| `save(data?)` | Notify the host that data changed so the detail view re-fetches |
| `markDirty()` | (v1.0.4+) Flag the tab as having unsaved edits, enabling the panel's own **Save** button |
| `onSave(handler)` | (v1.0.4+) Register a handler the panel awaits when **Save** is clicked; see below |

Tabs are filtered by `library`, so a `games`-only tab does not appear in the GOG
panel. Return an optional cleanup function from `mount` to tear down listeners
when the user switches away from the tab.

#### Saving through the panel's own Save button (v1.0.4+)

Instead of persisting immediately, a tab can let the user save its edits with the
panel's existing **Save** button (one request, no separate button). Hold your
edits in a working copy, call `ctx.markDirty()` whenever they change (this enables
the Save button), and register a handler with `ctx.onSave()`. The handler returns
a partial PATCH payload that the panel folds into its single save request:
`meta_ratings` is shallow merged (a `null` value deletes that key), other fields
are assigned.

```javascript
mount(el, ctx) {
  let tier = ctx.game.meta_ratings?.protondb || null;
  // ... build UI; on every change: tier = ...; ctx.markDirty && ctx.markDirty();

  ctx.onSave && ctx.onSave(() => ({
    meta_ratings: { protondb: tier || null }   // null -> key removed
  }));
}
```

Both `markDirty` and `onSave` are optional - guard them (`ctx.onSave && ...`) so the
tab still works on cores before v1.0.4, e.g. by falling back to your own button that
calls `gd.api.patch(ctx.apiPrefix + '/' + ctx.game.id, { ... }).then(() => ctx.save())`.

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

For plugins that fetch game metadata from external sources. These hooks work across all libraries - GOG, Games Library, and ROM Library.

| Hook | Returns | Description |
|------|---------|-------------|
| `metadata_provider_name()` | `str` | Display name (e.g. "PPE.pl") |
| `metadata_provider_id()` | `str` | Unique ID (e.g. "ppe") |
| `metadata_search_game(query)` | `list[dict]` | Search results |
| `metadata_get_game(provider_game_id)` | `dict or None` | Full game metadata |
| `metadata_get_cover_url(provider_game_id)` | `str or None` | Cover image URL |
| `metadata_get_covers(query)` | `list[dict]` | Cover/box art images for a game title |
| `metadata_get_heroes(query)` | `list[dict]` | Hero/background/fanart images |
| `metadata_get_logos(query)` | `list[dict]` | Clear logo / wheel images |

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

Used by `metadata_get_game()`. Fields are used in the Description and Details tabs of the Edit Metadata panel. The `rating` field (0-10 scale) is saved and displayed as a badge on game detail pages.

```python
{
    "provider_id": "ppe",
    "provider_game_id": "https://www.ppe.pl/gry/Game/123",
    "title": "Game Title",
    "description": "Full description text",
    "rating": 8.5,           # 0-10 scale, shown as badge on game detail
    "genre": "FPS",
    "release_date": "2024-01-15",
    "developer": "Studio Name",
    "publisher": "Publisher Name",
    "release_year": 2024,
    "genres": ["FPS", "Action"],
    "player_count": "1-4",
    "screenshots": ["https://example.com/screen1.jpg", ...],
    "source_url": "https://www.ppe.pl/gry/Game/123",
}
```

### Image result dict

Used by `metadata_get_covers()`, `metadata_get_heroes()`, and `metadata_get_logos()`. The `_source` field is used to resolve the plugin logo for source badges.

```python
{
    "url": "https://example.com/cover.jpg",      # full-size image
    "thumb": "https://example.com/cover_sm.jpg",  # thumbnail (can be same as url)
    "type": "static",                              # "static" or "animated"
    "label": "Box Art - Front",                    # display label
    "author": "username",                          # optional credit
    "_source": "myplugin",                         # provider ID (used for logo badge)
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
