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
| `frontend_get_routes()` | `list[dict] or None` | Custom pages (nav entry + URL); pair with `__GD__.registerRoute` in `frontend_get_js` |

### Custom pages (`frontend_get_routes`)

A plugin can add its own full page with a menu entry. Return a list of routes
from `frontend_get_routes()`; each becomes `/x/<path>` and shows up in the user
menu (and in any theme that reads `__GD__.pluginRoutes`):

```python
@hookimpl
def frontend_get_routes(self):
    return [{"path": "my-page", "label": "My Page", "icon": "mdi-puzzle"}]
```

Render the page from `frontend_get_js()` by registering a mount function against
the same path. GD calls it with the host element and passes `{path, api, t}`;
return an optional cleanup function:

```python
@hookimpl
def frontend_get_js(self):
    return r"""
(function () {
  var gd = window.__GD__;
  if (!gd || typeof gd.registerRoute !== 'function') return;
  gd.registerRoute({
    path: 'my-page',
    mount: function (el) {
      el.innerHTML = '<h1 style="padding:24px">Hello from my plugin</h1>';
      return function () { el.innerHTML = ''; };   // optional cleanup
    }
  });
})();
"""
```

The page is reachable at `/x/my-page`. Aggregated routes are served from
`GET /api/plugins/frontend/routes` (consumed by the SPA at startup).

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

### Vuetify components available to a theme - changed in v1.0.31

The app registers three Vuetify components globally: `VApp`, `VBtn` and
`VSnackbar`. Before v1.0.31 it registered the entire library, so a theme could
reach for any `<v-*>` tag and find it.

Nothing shipped was using one - neither Neon Horizon nor Vapor contains a
single `<v-*>` tag, and the app itself uses only those three - but if your
theme renders, say, `<v-data-table>`, it will no longer resolve.

Vuetify's directives (`v-ripple` and friends) are still registered and are
unaffected. The stylesheet is unchanged, so `.v-application` and the rest of
the Vuetify class names still exist.

If you need another component, import and register it in your own theme rather
than expecting the host to provide it. That is the more robust arrangement in
any case: it keeps your theme working regardless of what the host registers.

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

**Gotchas of the compiled pipeline:**
- **Always bind image sources** (`:src="'/path.png'"`), never a static
  `src="/path.png"` - the compiler rewrites static asset references and a
  plain `src` can end up stripped from the bundle.
- Only import from `vue`, `vue-router` and your own local `.vue` files -
  anything else is not resolvable at runtime.
- Pinia reactivity may not cross the plugin boundary - snapshot into local
  refs and refresh on the `gd-theme-updated` event (see above).

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
    resolveDetailRows(game, library),  // consumer side for themes with own detail pages (v1.0.15)

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

    // Unified, library-aware add-content actions (v1.0.17) - see "Library actions API" below
    library: {
        createGame({ title, library }),                       // -> game (has .id)
        uploadFile(gameId, file, { os, fileType, onProgress }),
        uploadFromUrl(gameId, { url, os, fileType }),         // -> { id, filename }
        addTorrent({ source, title, os, library, isFile }),  // -> download record
        scan(librarySlug?),                                   // -> { created, updated, ... }
        addByUpload({ library, title, file, os, fileType, onProgress }),  // create + upload
    },

    // Theme-declared home sections (v1.0.15; writes v1.0.26) - see "Theme home sections" below
    homeSections: {
        register(sections),           // register([{id, label}]) -> unregister()
        list(),                       // the active theme's registered sections
        isHidden(id),                 // has the user switched this section off?
        order(ids),                   // ids sorted into the user's chosen order
        isOptionOn(sectionId, optId, default?),  // a per-section switch
        setOrder(ids),                // persist the order the user arranged
        setHidden(id, hidden),        // show or hide one section (idempotent)
        toggle(id),                   // flip one section's visibility
        setOption(sectionId, optId, on),  // set a per-section switch
        reset(),                      // drop this theme's layout, back to register()
    },

    // Settings blocks the theme edits itself (v1.0.26) - see "Owning a Settings block" below
    managedSettings: {
        register(keys),  // register(["homeSections", ...]) -> unclaim()
        isManaged(key),  // does the active theme edit this setting itself?
    },

    // Shared editors and styled dialogs - see "Shared editors and dialogs" below
    ui: {
        openMetadataEditor({ game, apiPrefix?, onSaved?, onClosed? }),
        closeMetadataEditor(),
        openCollectionEditor(collectionOrSlug, { onUpdated?, onDeleted?, onClosed? }),
        closeCollectionEditor(),
        openRomMetadataEditor({ rom, onSaved?, onClosed? }),   // v1.0.15
        closeRomMetadataEditor(),
        confirm(msg, opts?),  // styled confirm dialog -> Promise<boolean> (v1.0.15)
        alert(msg, opts?),    // styled alert dialog (v1.0.15)
        openAbout(),          // the shared About dialog (v1.0.15)
    },

    // Read-only server progress events (v1.0.15) - see "Server progress events" below
    events: {
        on(event, cb),        // subscribe to a whitelisted event -> unsubscribe fn
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

`isHidden` is the read side of the per-user library visibility Settings offers; a
theme that draws its own control for it must claim `"libraryVisibility"` (see
**Owning a Settings block** below).

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
recent.set(['games','gog']); // persist the per-theme selection
```

A theme that offers its own picker for this must claim `"recentLibraries"` (see
**Owning a Settings block** below), or the same switch ends up in two places.

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

### Library actions API (`window.__GD__.library`) - v1.0.17

Adding content to a library - create a game, upload a file, upload from a URL,
add a torrent, scan a folder - is **the same operation in every theme**. Rather
than each theme re-implementing raw `api.post()` calls (and re-implementing
library targeting each time), call this shared API. Your theme keeps its own
dialogs and progress UI; the API owns the endpoint shapes and the library
targeting rules (folder, membership, and keeping the game out of the default
Games library).

The `library` argument is a library slug. `"games"`, `""`, `null` and `undefined`
all mean the built-in Games library; a folder-backed custom library's slug routes
the game (and its files, and any torrent that finishes) into that library.

```javascript
const lib = window.__GD__.library;

// Create a game in the current library
const game = await lib.createGame({ title: "My Game", library: currentSlug });

// Upload a local file to it (onProgress gets 0-100)
await lib.uploadFile(game.id, file, {
  os: "windows", fileType: "game",
  onProgress: (percent) => { progress.value = percent; },
});

// Convenience: create + upload in one call (used by themes with a file-only dialog)
await lib.addByUpload({
  library: currentSlug, title: "My Game", file,
  os: "windows", fileType: "game",
  onProgress: (p) => { progress.value = p; },
});
```

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `createGame` | `({ title, library? })` | game object (has `.id`) | Also accepts optional `slug`, `description`, `description_short`, `developer`, `publisher`, `genres`, `tags`. |
| `uploadFile` | `(gameId, file, { os?, fileType?, language?, version?, onProgress? })` | file record | Destination folder follows the game's library automatically. `onProgress(percent, ev)`. |
| `uploadFromUrl` | `(gameId, { url, os?, fileType?, language?, version? })` | `{ id, filename }` | Server downloads in the background; follow the `upload:url_progress\|complete\|error` events keyed on the returned `id`. |
| `addTorrent` | `({ source, title, os?, library?, isFile? })` | download record (has `.id`, `.percent`) | `source` is a magnet/URL string, or a `File` when `isFile: true`. When the download finishes it auto-registers into `library`. Follow `torrent:download_*` events keyed on `id`. |
| `scan` | `(librarySlug?)` | `{ created, updated, errors, libraries }` | With a slug, scans only that library's folder; without one, scans the built-in Games folder plus every folder-backed custom library. |
| `addByUpload` | `({ library?, title, file, os?, fileType?, language?, version?, onProgress? })` | game object | `createGame` + `uploadFile` for the common file-only add flow. |

The URL-upload and torrent flows report progress over socket.io - subscribe with
`window.__GD__.events.on(...)` (see **Server progress events** below).

This API is v1.0.17+, so a theme that uses it must set `"min_gd_version":
"1.0.17"` in `plugin.json` (the store install gate enforces it). If you prefer to
keep a lower minimum, feature-detect instead and hide the add/upload controls
when `window.__GD__.library` is absent.

#### Packaging a game's files - `package` / `packable` (v1.0.19)

An admin can bundle a library game's loose files into archives: one per group
(each OS platform, plus extras and DLC), or everything into a single combined
archive. This is the same operation the core Package dialog uses, so a theme can
offer its own Package button and drive it directly. Works for GOG, custom, and
admin custom-library games.

```javascript
const lib = window.__GD__.library;

// Which groups have something to bundle right now (a folder with 2+ files).
// Returns group labels, e.g. ["windows", "linux", "extras", "dlc"].
const groups = await lib.packable(game.id);

// Package selected groups - each becomes its own download:
//   {Title}.zip per OS platform, extras.zip, dlc.zip
await lib.package(game.id, { groups, deleteOriginals: false });

// Or bundle EVERYTHING into one combined {Title}.zip
await lib.package(game.id, { singleArchive: true, deleteOriginals: true });
```

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `packable` | `(gameId)` | `string[]` | Group labels worth bundling (a folder with 2+ files: `windows` / `mac` / `linux` / `extras` / `dlc`). Empty when nothing is packable, so a theme can show or hide its Package button. |
| `package` | `(gameId, { groups?, deleteOriginals?, singleArchive? })` | `{ ok, started, platforms }` | Omit `groups` to package every group. `singleArchive: true` combines all files into one `{Title}.zip` (available even when no single folder has 2+ files). `deleteOriginals` removes the loose files after zipping (overrides the global setting). Admin-only. |

Extras and DLC are bundled even when their files are already individual `.zip`
archives (glued, not re-compressed); a group with a single file is not offered.
Packaging runs in the background: `package()` returns `{ started, platforms }`
right away (it does not wait for the archives to finish). Follow progress on the
`download:packaging` socket event with `__GD__.events.on("download:packaging", cb)`
- the payload carries `{ id, status: "packaging" | "completed" | "failed", done,
total }`. That event is exposed to plugins since GD **1.0.24**; on older cores it
is not in the plugin event whitelist, so feature-detect (or just show a brief
"packaging..." state after the call resolves, like the built-in Package dialog).
The `package()` API itself requires `"min_gd_version": "1.0.19"`.

#### GOG library sync and clearing metadata (v1.0.23)

The GOG library is not folder-scanned like custom libraries; it syncs from the
connected GOG account and adopts already-downloaded games. A theme can drive the
GOG library toolbar (start a sync, clear its scraped metadata) through this API
instead of hand-rolling the `/gog/library/*` endpoints, and can clear a single
game's metadata from any library. All four are admin-only.

```javascript
const lib = window.__GD__.library;

// Start a GOG sync: pull the connected account, adopt already-downloaded games,
// and (unless disabled) scrape metadata. Runs server-side; poll for progress.
await lib.gogSync({ autoScrape: true, forceRescrape: false });

let s = await lib.gogSyncStatus();   // { running, phase, synced, adopted, error }
while (s.running) {
  // update your UI from s.phase ("adopt" | "scrape"), s.synced, s.adopted
  s = await lib.gogSyncStatus();
}

// Clear ALL scraped metadata from the GOG library (the games stay)
await lib.gogClearMetadata();

// Clear ONE game's scraped metadata so it can be re-scraped from scratch.
// kind is "games" (Games / custom library), "gog", or "rom".
await lib.clearGameMetadata("games", game.id);
```

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `gogSync` | `({ autoScrape?, forceRescrape? })` | `void` | Pull the connected GOG account, adopt already-downloaded games, and (unless `autoScrape: false`) scrape metadata. `forceRescrape: true` re-scrapes games that already have metadata. Runs server-side; poll `gogSyncStatus()`. Admin-only. |
| `gogSyncStatus` | `()` | `{ running, phase, synced, adopted, error }` | Current (or last) sync state. `phase` is `"adopt"` or `"scrape"`. Poll while `running` is true. |
| `gogClearMetadata` | `()` | `void` | Remove all scraped metadata from the GOG library (keeps the games). Admin-only. |
| `clearGameMetadata` | `(kind, id)` | `void` | Clear a single game's scraped metadata (title, source and files are kept) so it can be re-scraped. `kind` is `"games"`, `"gog"` or `"rom"`; the endpoint differs per source, so the API dispatches to the right route. Admin-only. |

Requires `"min_gd_version": "1.0.23"`. Feature-detect
(`typeof lib.gogSync === "function"`) if you want a lower minimum and hide these
controls on older cores.

### Storefront catalogues - `window.__GD__.catalog` (v1.0.27)

A store library (`is_store`, fed by a `LibraryCatalogSpec` plugin - see that
spec) is not an ordinary library: its shelf is the *catalogue*, and a game exists
only once somebody pulls a build. A theme that renders a store library with the
normal library data shows only the handful already downloaded and offers no way
to reach the catalogue - which is how the store worked in one theme out of four
before this API. Bring your own shelf layout and call `__GD__.catalog` for the
data.

```js
// A store library carries a catalog_id; that string is the catalogue key.
const stores = __GD__.stores.libraries().filter(l => l.is_store && l.catalog_id)
const catalogId = stores[0].catalog_id

const entries = await __GD__.catalog.listEntries(catalogId)   // the whole shelf
const entry   = await __GD__.catalog.getEntry(entryId)        // one, with detail
await __GD__.catalog.download(entryId, { assets: ['Game-win64.zip'] })
await __GD__.catalog.sync(catalogId)            // admin: re-read from source
await __GD__.catalog.clearMetadata(catalogId)   // admin: wipe scraped metadata
const all = await __GD__.catalog.listCatalogs() // every registered catalogue
```

| Method | Returns | Notes |
|--------|---------|-------|
| `listEntries(catalogId)` | `CatalogEntry[]` | Everything the catalogue offers |
| `countEntries(catalogId)` | `number` | How many entries the catalogue holds, without fetching them - for a card that shows only the count |
| `getEntry(entryId)` | `CatalogEntry` | One entry with full detail |
| `download(entryId, {assets?})` | `object` | Turn the offer into a game and pull builds; omit `assets` for the entry's default |
| `sync(catalogId)` | `object` | Admin only, server-side; re-read the catalogue |
| `clearMetadata(catalogId)` | `{cleared}` | Admin only; reset every listing's scraped metadata |
| `listCatalogs()` | `object[]` | Every catalogue the installed plugins registered |

A `CatalogEntry` carries the same presentation a GOG game does, so a store tile
reads like a library tile: `id`, `title`, `subtitle`, `cover_path` (falls back to
the square `icon_path`), `background_path`, `logo_path`, `description`,
`developer`, `publisher`, `release_date`, `rating` (0-5), `genres`,
`screenshots`, `meta_ratings`, plus the store-specific fields:

| Field | Meaning |
|-------|---------|
| `downloaded` | `true` once a build has been pulled - the offer is now a game. Render an "owned" badge and route to the game. |
| `library_game_id` | The game it became (`null` until downloaded). Open a downloaded entry at the game's own detail route, not the store's. |
| `assets` | The builds on offer (`[{name, os, size, url}]`), for a download picker. Pass the chosen names to `download()`; the built-in themes share a `CatalogDownloadDialog.vue` you can copy, but nothing stops a theme building its own. |
| `available` / `unavailable_reason` | A listing the catalogue can no longer offer, and why. |

Open an *offer* (not yet a game) at the store's entry route,
`/lib/{storeSlug}/entry/{entryId}`. See `CatalogStoreView.vue` (Modern/Classic)
and `NeonHorizonStore.vue` for a full store view built entirely on this API.

Requires `"min_gd_version": "1.0.27"`. Feature-detect
(`typeof __GD__.catalog?.listEntries === "function"`) for a lower minimum.

### ROM sources - `window.__GD__.romSources` (v1.0.29)

A ROM source is a remote catalogue of ROMs a `RomSourceSpec` plugin describes
(see that spec). It is not a storefront: nothing is pre-synced, because a source
can stand in front of tens of thousands of ROMs. A theme asks for the sources,
drills into a platform, lists ROMs a page at a time and asks for a download; core
owns the fetch, the write into `roms/<fs_slug>/` and the scan plus scrape that
follow. Every endpoint behind this API is admin-only (`LIBRARY_ADMIN`), so gate
the entry point on the same thing.

```js
const sources = await __GD__.romSources.list()
const src = sources[0]
if (src.requires_auth && src.configured === false) {
  /* send the user to the plugin's settings; listing would 409 */
}

const plats = await __GD__.romSources.platforms(src.id)
const page  = await __GD__.romSources.listRoms(src.id, 'snes', {
  page: 1, pageSize: 60, query: 'mario', region: 'USA',
  collection: 'No-Intro (2025)', format: 'zip', kind: 'retail',
})
await __GD__.romSources.download(src.id, [page.items[0].id])
```

| Method | Returns | Notes |
|--------|---------|-------|
| `list()` | `RomSource[]` | Every source the installed plugins registered |
| `platforms(sourceId)` | `RomSourcePlatform[]` | Already filtered to slugs GD knows |
| `listRoms(sourceId, fsSlug, opts)` | `RomSourceListing` | One live page; see the options below |
| `download(sourceId, ids, {force?})` | `{queued, skipped}` | One id or many. `force` re-downloads over a file that is already there |
| `previewEntry(fsSlug, entry)` | `RomSourcePreview` | Cover and facts for ONE row the user asked about |
| `previewKey(fsSlug, entry)` | `string` | Cache key for the above, keyed on the game |
| `route(sourceId, fsSlug?)` | `string` | Canonical in-app route, so the URL layout stays the core's |
| `platformArt(fsSlug)` | `{icon, name, fanart}` | The same console art the Retro grid uses |
| `__GD__.roms.import(url, fsSlug, filename)` | `object` | General primitive: pull one ROM by URL, no adapter needed |

A `RomSource` carries `id`, `name`, `plugin_id`, `plugin_name`, `icon`,
`tile_bg`, `requires_auth` and `configured`. Head the view with `plugin_name`
and `icon` (the owning plugin's identity) and keep `name` as the catalogue
detail; `tile_bg` is the source's own tile art. When `requires_auth` is `true`
AND `configured` is `false`, listing is refused server-side with a 409, so gate
on the pair and render a "configure to enable" state instead of an empty grid.

An entry in `listing.items` carries `id`, `title`, `filename`, `region`, `size`,
`collection`, `format`, `kind`, `crc` / `md5` / `sha1` and `owned`. Two of those
are worth spelling out:

- `title` and `filename` are deliberately different. Arcade sets are named after
  the emulator (`mslug.zip`) and must keep that name on disk, so a source may
  resolve a real title for display while the file stays as it was.
- `owned` is decided by hash where the source published one, and by filename
  where it did not. Hashes are absent for an entry that arrives inside an
  archive, because there the source can only hash the wrapper.

The listing echoes back the `page` it answered for, alongside `items` and
`total`.

The listing also returns `collections`, `formats` and `kinds`: every value
available for that platform, whatever page was asked for. Use them as the
filter's options and pass a chosen value back as `collection` / `format` /
`kind`. A list with one entry or none has nothing to filter by, so hide the
control rather than showing a menu of one.

`previewEntry` costs a scraper call, so it is for a row the user pointed at, not
for a listing. Cache on `previewKey`, which keys on the game rather than the row:
"Sonic (USA)" and "Sonic (Europe)" collapse to one lookup. The preview always
returns `found`, `query` and `source`; on a hit it also carries `matched_by`
(`"hash"` or `"name"`), `name`, `summary`, `developer`, `publisher`, `genres`,
`release_year` and `cover_url`. A miss carries those three keys alone, so read
the rest behind `found`. The cover URL is already proxied, since a scraper URL
carries the account in its query string - render it as given, never rebuild it.

Downloads report over socket.io. Subscribe through `__GD__.events.on` and key on
the job `id` that `download()` handed back:

| Event | Payload |
|-------|---------|
| `romsource:download_progress` | `id`, `source_id`, `entry_id`, `fs_slug`, `filename`, `percent` (`-1` when the size is unknown), `received`, `total`, `speed` |
| `romsource:download_complete` | the same identity fields plus `rom_id` |
| `romsource:download_error` | the same identity fields plus `error` |

A cold source can be slow: a set spread over dozens of upstream items has to be
walked before the first page exists. `listRoms` therefore allows two minutes and
`platforms` the same. Show a loading state rather than a spinner that looks
stuck, and expect the second visit to be immediate.

Requires `"min_gd_version": "1.0.29"`. Feature-detect
(`typeof __GD__.romSources?.list === "function"`) for a lower minimum.

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

### registerDetailRow / resolveDetailRows - v1.0.10 / v1.0.15

`registerDetailRow(row)` lets ANY plugin add a row to the game detail card and
have the ACTIVE THEME render it natively (fonts, colors and layout follow the
theme - no DOM injection needed):

```javascript
window.__GD__.registerDetailRow({
  id: 'my-plugin-score',        // unique row id
  library: 'games',             // 'games' | 'gog' | 'all' (default 'all')
  resolve({ game, library }) {  // called per game; return null to skip the row
    return {
      label: 'My Score',                 // key column (omit with fullWidth)
      segments: [                        // declarative value content
        { text: '87 / 100', color: '#4ade80' },
      ],
      details: {                         // optional "Show details" expander
        toggleLabel: 'Show breakdown',
        items: [ [{ text: 'Story: 9' }], [{ text: 'Gameplay: 8' }] ],
      },
      color: '#4ade80',                  // row accent
      title: 'Tooltip text',
      fullWidth: false,                  // true = span the card, no label column
      // render(el, ctx) {}              // escape hatch: draw the value yourself
    };
  },
});
```

Themes that build their OWN detail pages call the consumer side (v1.0.15) and
render the resolved rows wherever they fit:

```javascript
const rows = window.__GD__.resolveDetailRows(game, 'games');
// -> [{ id, label?, segments?, details?, fullWidth?, color?, title?, class? }, ...]
```

A row whose `resolve` throws is skipped - a misbehaving plugin cannot break
the detail page.

### Shared editors and dialogs (`__GD__.ui`)

Themes that render their own detail pages still get the CORE editors (plugin
metadata tabs mount inside them, so they must stay shared components). Call:

```javascript
const ui = window.__GD__.ui;

// Game metadata editor. apiPrefix defaults to the game's library routes.
ui.openMetadataEditor({ game, onSaved(updated) {}, onClosed() {} });

// Collection editor (v1.0.12).
ui.openCollectionEditor(collectionOrSlug, { onUpdated() {}, onDeleted() {}, onClosed() {} });

// ROM metadata editor (v1.0.15) - the emulation twin of the game editor
// (ratings, time-to-beat, per-media upload/clear, search-by-title).
ui.openRomMetadataEditor({ rom, onSaved(updated) {}, onClosed() {} });
```

Saves also dispatch DOM events - `gd-game-updated`, `gd-collection-updated`
and `gd-rom-updated` (detail `{ id }`) - so passive views can refetch.

Styled dialogs (v1.0.15) replace browser-native `confirm()` / `alert()` so
plugins match every theme:

```javascript
const ok = await ui.confirm('Delete this?', { title: 'Delete', danger: true,
                                              confirmText: 'Delete', cancelText: 'Cancel' });
await ui.alert('Done!', { title: 'Info' });
```

`requireTick: true` (v1.0.32) keeps the confirm button disabled until the reader
ticks a checkbox, and focus lands on the tick rather than the button:

```javascript
const ok = await ui.confirm(body, { title: 'Delete', danger: true,
                                    requireTick: true });
```

The label is one of the core's own translations, so a plugin asking this way has
nothing to add to its own locale files. Two rules keep it worth something.

Use it where an answer destroys something nothing can fetch again - files on
disk, a save, a library entry - and put it on the **first** question of a flow
if that question is the one that acts. A flow that asks "delete this?" and then
"and the files too?" has already deleted the entry by the time the second
question appears, so the tick belongs on the first.

Do not use it on reversible actions. A tick in front of something harmless
teaches people to tick without reading, and then they tick without reading on
the question that mattered.

On cores older than 1.0.32 the option is ignored: the dialog opens as an
ordinary confirm, which is the pre-1.0.32 behaviour and safe to ship. Set
`min_gd_version` to `1.0.32` only if your plugin depends on the guard actually
being there.

`ui.openAbout()` (v1.0.15) opens the shared About dialog (logo, running GD
version, Discord invite) - add an "About" entry to your theme's user menu and
guard it with `if (__GD__.ui?.openAbout)` so the theme still works on older
cores.

### Theme home sections (`__GD__.homeSections`) - v1.0.15

A theme layout with its own home-page sections (a trailer shelf, genre tiles, or
the built-in "Continue playing" / "Recently played" rails) registers them to
declare what the user is allowed to arrange. By default Settings -> Libraries
then offers per-user on/off toggles **and reorder arrows** for them
automatically. A theme that ships its own on-page editor claims the block
instead (see **Owning a Settings block** below), and Settings draws nothing for
it - the setting is the same either way, only the surface differs.

Register from a **layout**, not a page view: the layout outlives navigation, so
the section list stays registered wherever the controls are drawn - Settings on
another route, or your own editor after the user has navigated away from the
page that renders the sections. Register on mount and call the returned
unregister on unmount.

```javascript
import { onMounted, onUnmounted } from 'vue';

let un = null;
onMounted(() => {
  un = window.__GD__.homeSections.register([
    { id: 'continue_playing', label: 'dashboard.continue_playing' },
    { id: 'recently_played',  label: 'dashboard.recently_played' },
    // Pin a section to a fixed spot: hide its reorder arrows.
    { id: 'hero', label: 'vp.sec_hero', orderable: false },
    // A section with its own per-user switch, on until the user touches it.
    { id: 'trailers', label: 'vp.sec_trailers',
      options: [{ id: 'autoplay', label: 'vp.autoplay', default: true }] },
  ]);
});
onUnmounted(() => un && un());
```

Section fields: `id` (stable id, also the per-user setting key), `label` (an
i18n key or a literal), `orderable` (default `true`; set `false` when the theme
lays the section out at a fixed spot and does not route it through `order()`, so
the section may be switched off but not moved), and `options[]` (per-section
switches `{ id, label, default? }` the user flips independently of the section's
own on/off). `orderable` and `options[]` are declarations rather than drawing
instructions: Settings honours them when it renders the block, and a theme that
has claimed
`homeSections` must honour them in its own editor - `orderable: false` means no
reorder control for that section, wherever the control lives.

Read the choices back and re-read on the `gd-theme-updated` DOM event (fired on
any toggle or reorder, whether it came from Settings or from the theme's own
editor) so the home page reacts live:

```javascript
const hs = window.__GD__.homeSections;

// Lay sections out in the user's chosen order (unmoved ids keep your order):
for (const id of hs.order(['continue_playing', 'recently_played'])) {
  if (hs.isHidden(id)) continue;                 // user switched this rail off
  renderRail(id);
}

// A per-section switch. The `default` declared in register() is the source of
// truth until the user toggles it, so pass the same default (or omit it):
if (hs.isOptionOn('trailers', 'autoplay', true)) startAutoplay();
```

The writes below fire that same event, so your own editor re-renders through the
identical path - snapshot into a local `ref` and refresh on the event plus a
light poll, exactly as in **Reactivity (compiled Vue themes)** above, rather
than hand-rolling a refresh after each write.

#### Arranging sections on the page - the write API (v1.0.26)

A theme can let the user arrange the home page in place - drag a shelf, hide
one, flip a switch - instead of sending them to Settings. These five writes
persist exactly what Settings persists, so the two surfaces remain one setting.
Pair them with `managedSettings.register(["homeSections"])` (see **Owning a
Settings block** below) so the same controls are not offered twice.

```javascript
const hs = window.__GD__.homeSections;

// Persist the order the user arranged.
hs.setOrder(['hero', 'recent', 'trailers']);

// Explicit show/hide - the right call for an editor that re-applies its whole
// state, because writing the value a section already holds is skipped.
hs.setHidden('trailers', true);

// Flip one section (always writes).
hs.toggle('trailers');

// A per-section switch declared in register()'s `options`.
hs.setOption('recent', 'flip', true);

// "Reset layout": drop order, hidden and options for this theme in one write.
hs.reset();
```

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `setOrder` | `(ids)` | `void` | Persists the arranged order (the array is copied). Ids you leave out keep the theme's own order, at the end - which is why a section that appears at runtime (a new collection, a library just created) shows up without invalidating a saved layout. Read back with `order(ids)`. |
| `setHidden` | `(id, hidden)` | `void` | Explicit show/hide. **Idempotent**: writing the value already held is skipped entirely - no save, no event - so an editor may cheaply re-apply its whole state. Read back with `isHidden(id)`. |
| `toggle` | `(id)` | `void` | Flips one section's visibility. Always writes, unlike `setHidden`. |
| `setOption` | `(sectionId, optId, on)` | `void` | Sets one of the switches declared in `options[]`. An option the user never touched stays **absent** rather than being written as `false`, which is what preserves the `default` fallback in `isOptionOn`. Always writes. |
| `reset` | `()` | `void` | Drops this user's whole layout for the ACTIVE theme - order, hidden and options - in a single write (one event, one save), falling back to what `register()` declared. The theme's other settings (skin, cover size, the recently-added choice, your own setting keys) are left intact. |

Every write persists per-user **and per-theme**, fires `gd-theme-updated`, and
schedules a debounced (1.2 s) save to the server - so a layout the user arranges
in one browser follows them to another. Because the event fires on your own
writes too, guard the expensive half of your handler while the editor is open:
Vapor re-reads its section state on every event but skips refetching its rails
while arrange mode is on, so a drag does not put two requests behind every
gesture.

No id is validated anywhere. An unknown id is stored verbatim and simply never
matches a registered section, so a typo costs a dead entry in the user's
settings rather than an error.

Methods: `register(sections)` -> `unregister()`, `list()` (the active theme's
sections; reactive - what Settings renders its block from, unless the theme has
claimed `homeSections`), `isHidden(id)`, `order(ids)` (ids sorted into the
user's chosen order), and `isOptionOn(sectionId, optId, default?)`, plus the
five writes above. The `orderable` field and the per-option `default` (source of
truth for `isOptionOn`) were added in 1.0.25; `setOrder`, `setHidden`, `toggle`,
`setOption` and `reset` were added in 1.0.26.

The writes and `managedSettings` are v1.0.26+, so a theme with an on-page editor
must set `"min_gd_version": "1.0.26"` in `plugin.json` (the store install gate
enforces it). If you prefer to keep a lower minimum, feature-detect instead
(`typeof hs.setOrder === "function"`, `!!window.__GD__.managedSettings`) and hide
the editor on older cores. Every call site optional-chains, so an editor left
enabled on 1.0.25 fails silently - it renders and responds while nothing
persists, and Settings goes on drawing its own block underneath.

### Owning a Settings block (`__GD__.managedSettings`) - v1.0.26

A theme that ships its own on-page editor for a setting **claims** it, and core
Settings stops drawing its controls for it. Without this the same switches live
in two places and quietly drift apart, leaving the user to work out which one
actually applies.

```javascript
import { onMounted, onUnmounted } from 'vue';

let unclaim = null;
onMounted(() => {
  // Vapor claims exactly this one: its home page arranges sections itself, and
  // deliberately leaves the other two blocks to Settings.
  unclaim = window.__GD__.managedSettings?.register?.(["homeSections"]) || null;
});
onUnmounted(() => { unclaim && unclaim(); unclaim = null; });
```

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `register` | `(keys)` | `unclaim()` | Claims the listed blocks for this theme. Keys already claimed are skipped, so the registry never holds duplicates. |
| `isManaged` | `(key)` | `boolean` | Is this block handled by the active theme? Reactive - usable directly in a `v-if`. |

The three keys, all of them blocks of Settings -> Libraries:

| Key | What Settings stops drawing |
|-----|-----------------------------|
| `"libraryVisibility"` | The per-user library on/off list (the write side of `stores.libraries().isHidden`). |
| `"recentLibraries"` | The picker for which libraries feed a "recently added" row - see **Recently-added rows** above. Its pre-existing condition still applies as well: the block never appears for the Classic layout. |
| `"homeSections"` | The theme home-section list with its visibility toggles, reorder arrows and per-section option switches. Its pre-existing condition still applies: the block only ever appears when the theme registered sections. |

**Claiming a key obliges you to replace it.** Settings draws nothing at all for
a claimed block, so a theme that claims `"homeSections"` without shipping an
editor takes the controls away and puts nothing in their place.

The registry is module-level and in-memory: it is not persisted, it is gone on
reload, and it is **not** cleared when the user switches theme. The theme owns
the unclaim - call it on unmount, the same mount/unmount discipline as
`homeSections.register`. The returned function removes only the keys that call
actually added, so registering a key something else already claimed hands back a
no-op unclaim and cannot strip the other claim.

Only the three keys above are honoured. The runtime accepts any string, so a key
outside the list is stored and then nothing ever reads it.

### Dashboard and saves (`__GD__.dashboard`) - v1.0.25

A theme that renders its own dashboard, save manager, or request queue reads and
writes through `window.__GD__.dashboard`. Every call is scoped and gated on the
server exactly like the built-in screen, so calling these directly cannot widen
access - the admin-only calls return `403` for a non-admin.

```javascript
const dash = window.__GD__.dashboard;

// Overview data (see the Dashboard wiki page for the payload shapes):
const mine  = await dash.me({ days: 7 });            // the caller's own stats
const admin = await dash.admin({ days: 30 });        // admin only
const q     = await dash.queue();                    // admin: live transfer snapshot

// Live feed (admin only). Each returns an unsubscribe function - call it on unmount.
const offQ = dash.onQueue((q) => renderQueue(q));    // dashboard:queue pushes
const offH = dash.onHealth((h) => renderHealth(h));  // dashboard:health heartbeat

const who = await dash.gameDownloaders(gameId);      // admin: who downloaded a game
```

`me(params)` accepts `{ days }` (1 / 7 / 30) or `{ start, end }`, plus an optional
`sections` array (`downloads`, `continue_playing`, `recently_played`, `requests`)
so you compute only what you render.

Save management (the caller's own saves) and the request queue live on the same
object:

```javascript
const s = await dash.saves();                        // your states + battery saves + quota
await dash.exportSaves();                            // download a full backup zip
await dash.exportSaves(romId);                       // just one game's saves
await dash.importSaves(file);                        // restore from a gd-saves zip
await dash.exportSaveState(id);                      // one save as a zip
await dash.deleteSaveState(id);
await dash.deleteBatterySave(id);

const reqs = await dash.requests();                  // requests (admin: all; user: own)
await dash.setRequestStatus(id, { status: 'approved' });  // admin
await dash.deleteRequest(id);                        // admin
```

### Server progress events (`__GD__.events`) - v1.0.15

A narrow, read-only bridge to server Socket.IO progress events (the raw socket
stays off-limits). Only whitelisted events can be subscribed:

```javascript
const off = window.__GD__.events.on('upload:url_progress', (data) => { ... });
// later: off()
```

| Event | Fired |
|-------|-------|
| `torrent:download_progress` / `_complete` / `_error` | torrent-based game downloads |
| `upload:url_progress` / `_complete` / `_error` | server-side URL uploads |
| `download:packaging` (v1.0.24) | file-packaging jobs from `__GD__.library.package()` - `{ id, status, done, total }` |

### Emulation data for theme pages - v1.0.15

Endpoints a theme can build Retro / home ROM sections from (all through
`__GD__.api`, auth attached automatically):

| Endpoint | Returns |
|----------|---------|
| `GET /roms/recent?limit=N` | Latest ROMs as full tile dicts: `id, name, platform_slug, platform_fs_slug, platform_name, cover_path, background_path, wheel_path, release_year, genres, player_count, fs_size_bytes, created_at, rating_agg` |
| `GET /roms/top-rated?limit=N` | Same tile shape, ranked by `rating_agg` (aggregate 0-5 from ScreenScraper / IGDB / LaunchBox / plugin ratings) |
| `GET /roms?platform_slug=X&limit=N` | A platform's catalogue (list items do NOT carry platform fields - enrich client-side) |
| `POST /roms/platforms/{slug}/scrape?mode=new\|missing\|force` | Batch scrape: `new` = unidentified only, `missing` = fill per-field gaps only (existing data and media untouched), `force` = overwrite everything |
| `POST /roms/{id}/media/{kind}/upload` | Multipart upload of `cover/background/support/wheel/bezel/steamgrid/video` (+`screenshot` appends) |
| `PATCH /roms/{id}` | Metadata update; an EMPTY STRING on a `*_path` field clears that media (column + file), `null`/absent = no change |

`window.__GD__.getEjsCore(platformFsSlug)` tells whether a platform is
playable in the browser (returns the EmulatorJS core name or `null`).

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
| `metadata_provider_ratings()` | `bool` | Does this provider return numeric 0-10 ratings? (v1.0.15, see below) |
| `metadata_search_game(query)` | `list[dict]` | Search results |
| `metadata_get_game(provider_game_id)` | `dict or None` | Full game metadata |
| `metadata_get_cover_url(provider_game_id)` | `str or None` | Cover image URL |
| `metadata_get_covers(query)` | `list[dict]` | Cover/box art images for a game title |
| `metadata_get_heroes(query)` | `list[dict]` | Hero/background/fanart images |
| `metadata_get_logos(query)` | `list[dict]` | Clear logo / wheel images |
| `metadata_search_collection(query)` | `list[dict]` | Search collections / franchises / series by name (v1.0.12) |
| `metadata_get_collection(provider_collection_id)` | `dict or None` | Full metadata for one collection (v1.0.12) |

Since v1.0.26, `metadata_provider_name()` is also what LABELS your ratings in
the UI. A rating you supply is matched back to your plugin by
`metadata_provider_id()` and labelled with the name this hook returns,
everywhere it is shown: the ROM and game detail pages and both metadata
editors. Return it in presentation form ("PPE.pl") - it is used exactly as
given. Implement it: without the hook the label falls back to your provider id
in capitals.

### metadata_provider_ratings - v1.0.15

Providers whose `meta_ratings` values are numeric 0-10 game scores return
`True` (or simply omit the hook - that is the default): their entries are
rendered as scores, feed the aggregate rating and are editable in the rating
editors. A provider whose values are badges or tiers rather than scores
(a compatibility status, a certification, ...) MUST implement the hook and
return `False`, otherwise its entries would surface as fake ratings:

```python
@hookimpl
def metadata_provider_ratings(self) -> bool:
    return False
```

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

### Collections - `metadata_search_collection` / `metadata_get_collection` (v1.0.12)

A *collection* is a grouping of related games - a franchise or series (e.g. "Mass
Effect", "Final Fantasy"). If your provider knows about franchises, implement
these two hooks and the Collections feature can scrape collection info and
artwork the same way it scrapes games.

```python
@hookimpl
def metadata_search_collection(self, query: str) -> list[dict]:
    # search franchises/series by name
    return [{
        "provider_id": "myplugin",
        "provider_collection_id": "franchise/mass-effect",
        "name": "Mass Effect",
        "snippet": "Sci-fi RPG series by BioWare",   # optional
        "cover_url": "https://.../me.jpg",            # optional
        "start_year": 2007,                            # optional
        "end_year": 2021,                              # optional
    }]

@hookimpl
def metadata_get_collection(self, provider_collection_id: str) -> dict | None:
    # full metadata for one collection (the id returned by search above)
    return {
        "provider_id": "myplugin",
        "name": "Mass Effect",
        "description": "Full description...",       # optional
        "description_short": "Sci-fi RPG series",   # optional
        "cover_url": "https://.../me.jpg",          # optional
        "hero_url": "https://.../me_hero.jpg",      # optional
        "logo_url": "https://.../me_logo.png",      # optional
        "start_year": 2007,                          # optional
        "end_year": 2021,                            # optional
        "rating": 4.5,                               # optional, 0-5 scale (see note)
        "source_url": "https://.../mass-effect",    # optional
    }
```

Two things to know:

- **Rating scale differs.** `metadata_get_collection`'s `rating` is on a **0-5**
  scale, unlike `metadata_get_game`'s `rating`, which is **0-10**. Do not mix them.
- **Artwork hooks are reused for collections.** There are no separate collection
  artwork hooks - the Collections editor calls your `metadata_get_covers`,
  `metadata_get_heroes` and `metadata_get_logos` with the **collection name** as
  the `query` (instead of a game title). If your image hooks only understand game
  titles, either handle franchise names too or return an empty list for them.

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

Registered providers are discoverable at `GET /api/plugins/download/providers`
(with `?game_id=` reporting `can_handle`), started via
`POST /api/plugins/download/providers/{id}/start`, and polled via
`GET /api/plugins/download/providers/{id}/status/{task_id}`.

---

## LibrarySourceSpec

For plugins that scan game libraries from various sources.

| Hook | Returns | Description |
|------|---------|-------------|
| `library_source_name()` | `str` | Display name |
| `library_source_id()` | `str` | Unique ID |
| `library_scan(path)` | `list[dict]` | Discovered games/ROMs |

Registered sources are listed at `GET /api/plugins/library/sources` and scanned
via `POST /api/plugins/library/sources/{id}/scan`.

---

## LibraryCatalogSpec

For plugins that publish a **catalogue**: a listing of games the server *could*
hold, rather than files it already has. A `LibrarySourceSpec` scans a path for
what is here; a catalogue describes what is available elsewhere, so the library
it feeds is a **storefront** (the `is_store` flag) instead of a shelf. GOG is the
built-in example; this spec lets a plugin add others - the PC Ports catalogue is
one.

The plugin only *describes*. Core owns every write: it upserts the entries,
downloads artwork through the SSRF guard and serves it locally, creates the store
library, and decides membership - so a catalogue cannot hot-link a CDN image into
the UI or push a row past the guards. An admin cannot hand-make a store either; a
store is the plugin's to create.

| Hook | Returns | Description |
|------|---------|-------------|
| `library_catalog_id()` | `str` | Stable key for this catalogue in the database |
| `library_catalog_name()` | `str` | Display name (e.g. "GitHub PC Ports") |
| `library_catalog_library()` | `dict` | Optional store-library declaration (see below) |
| `library_catalog_fetch()` | `list[dict]` | The whole catalogue, one dict per entry |

`library_catalog_fetch` runs in a worker thread, so blocking HTTP is fine and
expected. Report a dead source per entry (`available: false`) rather than
raising - one gone repository must not cost the other seventy-six.

### The store-library declaration (`library_catalog_library`)

Optional. Core upserts a library from what you return and marks it a store fed by
this catalogue. Any key may be omitted; return nothing to take every default from
the id and name.

| Key | Type | Default | Notes |
|-----|------|---------|-------|
| `slug` | `str` | from the id | Stable route slug |
| `name` | `str` | the catalogue name | Display name |
| `icon` | `str` | - | Icon path or URL |
| `color` | `str` | - | Accent colour |
| `storage_folder` | `str` | the name | Folder under `data/games` for downloaded builds |

Downloaded games show in the **Games** library; only their *files* live under
`storage_folder` (e.g. `data/games/PC Ports/<title>/<os>/`).

### The store lifecycle

The store is created by the catalogue's first sync, so until then there is no
store page to open. That first sync is run from the plugin's configuration panel
in **Settings > Plugins** (its **Sync catalogue** button), which is where the
plugin's token or other config is entered; once the store exists, its own page
can sync too.

The store belongs to the plugin. Uninstalling the plugin deletes the store and
its listings, while every game already downloaded from it stays in the Games
library with its files and metadata. Disabling the plugin keeps the store.
Reinstalling and syncing rebuilds the store and re-links the fresh listings to
the games downloaded earlier, matched by the origin recorded on each game, so a
game already on the server is marked owned rather than offered again and each
listing regains the cover and metadata its game holds. This is why `external_id`
must be stable: it is the identity a re-link keys on.

### The entry dict (`library_catalog_fetch`)

| Key | Type | Notes |
|-----|------|-------|
| `external_id` | `str` | **Required.** Stable identity inside this catalogue, and the key entries are matched on across syncs. Use something that survives a rename - a repository path, not a title. |
| `title` | `str` | **Required.** Display name. For a port this is the *game*, not the project: people look for "Mario Kart 64", not "SpaghettiKart". |
| `subtitle` | `str` | Qualifier shown under the title. What tells two builds of one game apart. |
| `catalog_title` | `str` | The name before any parsing; kept as a fallback for metadata lookups. |
| `category` | `str` | Optional grouping; stored as a tag. |
| `icon_url` | `str` | Artwork URL. Core downloads it locally. |
| `description` | `str` | Optional summary. |
| `homepage` | `str` | Optional link shown on the detail page. |
| `available` | `bool` | `false` when the entry cannot be offered now (repository gone, no usable release). |
| `unavailable_reason` | `str` | Why, shown to the admin. Required when `available` is `false`. |
| `release` | `dict` | Omitted when nothing is downloadable yet - see below. |

`release`:

| Key | Type | Notes |
|-----|------|-------|
| `tag` | `str` | The build's own name - a release tag, not an invented version. |
| `published_at` | ISO-8601 `str` | |
| `prerelease` | `bool` | |
| `assets` | `list[dict]` | Each: `name`, `size` (int bytes), `url`, `os` (`windows`\|`mac`\|`linux`\|`all`), optional `arch` (free-form), optional `digest` (checksum). |

An entry missing `external_id` or `title` is skipped and logged, never guessed
at. A duplicate `external_id` in one fetch keeps the first and logs the rest.

### The lifecycle of an entry (the GOG shape)

1. **Sync** (`POST /api/plugins/library/catalogs/{id}/sync`, admin) calls
   `library_catalog_fetch` and reconciles it into the store: new entries are
   inserted, changed ones updated, and an entry the catalogue stopped offering is
   marked unavailable - **never deleted**, because an admin may have downloaded it
   and its row is the only record of where it came from. A sync creates
   `catalog_entries` only; it does **not** create games.
2. **Download** (`POST /api/plugins/library/catalog-entries/{id}/download`, body
   `{assets?: [name, ...]}`) turns one listing into a real `LibraryGame` in the
   Games library, copies the scraped presentation onto it, then pulls the selected
   builds through the shared URL path (the SSRF guard, size ceiling and virus scan
   all apply). The entry's `library_game_id` is set and `downloaded` becomes
   `true`. Before this, the entry is not a game - invisible to users, never
   counted anywhere.
3. **The store stays the source of truth.** A metadata edit or re-scrape on the
   listing is pushed onto the downloaded game (description, art, rating, genres,
   screenshots, ...), so the two never drift. Title, subtitle and category are
   left alone on purpose: the sync stamps those from upstream every run, and
   pushing them would undo an admin's rename of the game.

### Endpoints

| Method + path | Scope | Purpose |
|---------------|-------|---------|
| `GET /api/plugins/library/catalogs` | read | Every catalogue the loaded plugins offer |
| `GET /api/plugins/library/catalogs/{id}/entries` | read | Every listing in one catalogue |
| `GET /api/plugins/library/catalogs/{id}/entries/count` | read | Just the entry count, without the listings |
| `GET /api/plugins/library/catalog-entries/{id}` | read | One listing, with detail |
| `POST /api/plugins/library/catalogs/{id}/sync` | admin | Re-read the catalogue from its source |
| `POST /api/plugins/library/catalog-entries/{id}/download` | upload | Turn a listing into a game and pull builds |
| `POST /api/plugins/library/catalogs/{id}/clear-metadata` | admin | Reset every listing's scraped metadata in the store |
| `POST /api/plugins/library/catalogs/{id}/scrape-metadata` | admin | (Re)scrape every listing |
| `POST /api/plugins/library/catalog-entries/{id}/scrape-metadata` | admin | (Re)scrape one listing |
| `PATCH /api/plugins/library/catalog-entries/{id}` | admin | Edit one listing (the metadata editor's Save) |
| `GET /api/plugins/library/catalog-entries/{id}/covers` \| `/screenshots` \| `/meta-sources` | admin | Editor pickers |

A theme does not call these directly - it uses `window.__GD__.catalog` (below),
which owns the read / sync / download shapes once for every theme.

---

## RomSourceSpec

Manifest `"type": "rom_source"`. For a plugin that puts a remote catalogue of
ROMs in front of the user and downloads single files from it into
`roms/<fs_slug>/`, where the existing scan and scrape pipeline takes over.

A ROM source is the opposite trade to a `LibraryCatalogSpec` storefront. A
storefront is synced into the database and browsed from there, which works
because it holds hundreds of listings. A source can stand in front of tens of
thousands, so nothing is stored: the plugin lists on demand, a page at a time,
and resolves one file when the user picks it. A downloaded ROM becomes an
ordinary `Rom` row - a source never owns a shelf, and uninstalling the plugin
takes nothing away.

| Hook | Returns | Description |
|------|---------|-------------|
| `rom_source_id()` | `str` | Stable id, e.g. `"archive-hearto"` |
| `rom_source_name()` | `str` | Display name of the catalogue |
| `rom_source_meta()` | `dict` | Presentation and state; every key optional |
| `rom_source_platforms()` | `list[dict]` | The platforms on offer |
| `rom_source_list(fs_slug, page, page_size, query, region, sort, **filters)` | `dict` | One live page |
| `rom_source_resolve_download(entry_id)` | `dict` | One entry to a concrete download |

`rom_source_list` and `rom_source_resolve_download` are called in a worker
thread, so blocking HTTP inside them is fine and expected.

### Presentation (`rom_source_meta`)

| Key | Meaning |
|-----|---------|
| `tile_asset` | Path under the plugin's `assets/` for the source's tile art, served through `/api/plugins/{id}/assets/{path}` |
| `icon_asset` | Path for a small icon shown beside the source. Defaults to the plugin's own `logo.png` / `logo.svg`, so ship one and you can leave this out |
| `requires_auth` | Whether the source needs credentials before it can list or download |
| `configured` | Whether the plugin currently has what it needs. `False` together with `requires_auth` makes core show "configure to enable" and refuse listing |

### Platforms

One dict per platform: `fs_slug` (required), `display` and `count` (both
optional). `fs_slug` must exist in GD's `PLATFORM_MAP`. Mapping the source's own
platform naming onto that slug is the plugin's job, and an unmapped slug is
dropped and logged rather than guessed into some folder - a ROM in the wrong
folder scrapes as the wrong game and boots in the wrong emulator.

### Listing

Return `items`, `total`, and optionally `collections`, `formats` and `kinds`
(every value available for the platform, whatever page was asked for - core
hands them to the theme as the filter options).

Each item: `id` (stable within this source, handed back to
`rom_source_resolve_download`), `title`, `filename`, and optionally `region`,
`size`, `crc`, `md5`, `sha1`, `collection`, `format`, `kind`.

Four fields repay a second look:

- **`title` and `filename` are separate on purpose.** The file has to keep the
  name the emulator expects, but nothing stops the listing showing a real title
  next to it. Core strips a region tag from `title` for display and shows the
  region as a badge.
- **`collection`** stamps an entry with the upstream set it came from, for a
  source that merges several sets covering the same platform.
- **`format`** is derived from the filename when omitted, so set it only when the
  extension would lie.
- **hashes** are what let core mark an entry as already owned *before* anything
  is downloaded. Publish them only for a bare ROM. GD hashes the ROM inside an
  archive, not the archive, so passing the wrapper's hash for a `.zip` compares
  two different numbers and quietly breaks owned-detection.

`sort` arrives as one of `name_asc`, `name_desc`, `size_desc`, `size_asc` (what
the built-in ROM list offers) or `None`. **Core never re-orders the page it gets
back**, so a value the plugin does not handle means the sort control silently
does nothing.

`collection`, `fmt` and `kind` arrive as filters, by keyword, and **only to a
plugin whose signature names them**. The hook gained filters after its first
release and will gain more; a plugin written against the older signature keeps
being called exactly as it was written instead of erroring on an argument it
never heard of. Declare the ones you support and ignore the rest.

### Resolving a download

Return `url` (the one ROM file, never a whole multi-GB archive), `filename`,
`fs_slug`, and optionally `headers` and `cookies` carrying the source's auth.
Core attaches them to a guarded download and never logs them.

> Prefer `cookies` over a `Cookie` header. An HTTP client drops the `Cookie`
> header when a redirect crosses hosts, which is exactly what archive.org does
> when it hands a download to a datanode; a cookie jar survives it. A `Cookie`
> header is accepted and folded into the jar for convenience.

Credentials are the plugin's own business. Declare them in `config_schema` with
`password`-type fields (those are redacted from non-admins), read them from the
stored config, and return ready-to-use headers or cookies - the secret never
leaves the backend and never reaches a browser.

### Endpoints

Every one of these is `LIBRARY_ADMIN`.

| Endpoint | Description |
|----------|-------------|
| `GET /api/rom-sources` | Every registered source |
| `GET /api/rom-sources/{id}/platforms` | The platforms one source offers |
| `GET /api/rom-sources/{id}/platforms/{fs_slug}/roms` | One live page (`page`, `page_size` max 200, `query`, `region`, `sort`, `collection`, `fmt`, `kind`) |
| `GET /api/rom-sources/preview` | Cover and facts for one row (`fs_slug` plus `title` / `filename` / `size` / `crc` / `md5` / `sha1`) |
| `POST /api/rom-sources/{id}/download` | Queue entries (`entry_ids`, `force`) |
| `POST /api/rom-sources/import` | Pull one ROM by URL (`url`, `fs_slug`, `filename`, `force`) |

A theme does not call these directly - it uses `window.__GD__.romSources`
(above), which owns the list / preview / download shapes once for every theme.

---

## FirmwareSourceSpec

For a plugin that can fetch emulator firmware. No manifest `type` of its own and
no dedicated plugin: every installed instance is asked, so a source, a metadata
provider or a theme can add these hooks to what it already does.

Firmware itself is core's business. The store, the upload from disk and the
delivery into the running emulator all work with no plugin installed at all,
because a ROM can be copied in by hand and a BIOS has to be no harder. What a
plugin adds is the option to fetch a file the user would otherwise go hunting
for.

Core deliberately keeps the parts that must not be delegated. It decides which
filenames a core actually asks for, refuses anything else, and performs the
download itself behind the SSRF guard. A plugin hands over a URL and its own
credentials, never bytes from wherever it pleases.

| Hook | Returns | Description |
|------|---------|-------------|
| `firmware_source_name()` | `str` | Display name shown beside the offer, e.g. `"Internet Archive"` |
| `firmware_offers(libretro_core, paths)` | `dict` | Which of `paths` this plugin could supply |
| `firmware_resolve_download(libretro_core, path)` | `dict` | One file to a concrete download |

Both working hooks are called in a worker thread, so blocking HTTP inside them
is fine. `firmware_offers` runs whenever an administrator opens the firmware
screen, so keep it cheap.

### Cores are named the libretro way

`libretro_core` is the **libretro** core name (`puae`, `mupen64plus_next`,
`gambatte`), not the EmulatorJS one (`amiga`, `n64`, `gb`). That is how firmware
is catalogued everywhere else in GD, and several EmulatorJS names share one
core, so the libretro name is the only key that does not collide. Core does the
translation before calling you; the HTTP endpoints below still speak the
EmulatorJS name.

### Offering

`paths` holds only the files that are **missing on disk** for that core, so
there is nothing to filter out on your side and no reason to answer about a file
the user already has.

Return a dict keyed by the path, each value a dict:

| Key | Meaning |
|-----|---------|
| `label` | Optional. What the user is being offered, typically a set name |
| `size` | Optional. Bytes, if known without fetching |
| `md5` | Optional. Expected checksum, if the source publishes one |

Leave out anything you cannot supply. **A path that was not asked for is dropped,
not stored**: the same allow-list that guards uploads guards this, so a plugin
cannot slip a file in under a name the emulator core never wanted. Where two
plugins offer the same path the first one asked wins. A hook that raises, or
returns something other than a dict, is logged and skipped without disturbing the
other plugins or the screen.

### Resolving

Return `url` (that one file, direct), and optionally `headers` and `cookies`
carrying the source's own auth. Core attaches them to a guarded download and
never logs them. The first plugin to return a usable `url` wins.

The stored name is validated against core's own registry regardless of what you
return here. Credentials are your business, exactly as for a ROM source: declare
them in `config_schema` as `password`-type fields, read them from the stored
config, and hand back ready-to-use headers or cookies. The secret stays in the
backend and never reaches a browser.

> The redirect note from `RomSourceSpec` applies here too: prefer `cookies` over
> a `Cookie` header, because an HTTP client drops that header when a redirect
> crosses hosts.

### Endpoints

| Endpoint | Scope | Description |
|----------|-------|-------------|
| `GET /api/firmware/{ejs_core}/offers` | `LIBRARY_ADMIN` | What plugins say they could supply for the files still missing |
| `POST /api/firmware/{ejs_core}/fetch` | `LIBRARY_ADMIN` | Fetch one offered file and store it |

Both take the **EmulatorJS** core name in the path. An empty offers response is
the ordinary answer when nothing is missing, when no plugin offers anything, and
when no plugin is installed at all - the screen does not distinguish them.

---

## LifecycleSpec

For plugins that react to application events. `game` is a plain dict
(`{id, title, source, slug, gog_game_id}`); fetch anything more via the API
using `id`. Hooks are fired best-effort - a raised exception is logged and never
breaks the library write or the launch.

| Hook | Returns | Description |
|------|---------|-------------|
| `lifecycle_on_game_added(game)` | `None` | A game was added to the library (custom create / GOG publish / torrent finish) |
| `lifecycle_on_download_complete(game, path)` | `None` | A download finished (`path` = destination folder) |
| `lifecycle_on_play_start(game)` | `None` | A game/ROM was launched in the player |
| `lifecycle_on_play_end(game, seconds)` | `None` | A play session ended (`seconds` = elapsed play time) |
| `lifecycle_on_startup()` | `None` | Called on app start |
| `lifecycle_on_shutdown()` | `None` | Called on app stop |

> `lifecycle_on_startup` does not fire for a hot-loaded (folder-dropped) plugin -
> run one-time setup from the plugin's `__init__` instead.

### Recently-added notification (built in)

GamesDownloader sends its own rich "recently added" notification (Discord embed
+ optional email) when a game or ROM becomes ready - no plugin required. It is
controlled in **Settings > Notifications** (the *Recently added* toggles,
server name and templates). `lifecycle_on_game_added` fires alongside that
built-in delivery, so a plugin can react or route the event elsewhere on top of
it. ROM launches also expose `POST /api/roms/{id}/play/start|end`, which fire the
play hooks above.

---

## WidgetSpec

For plugins that add dashboard cards. Cards render on the built-in Dashboard
page (`/dashboard`) and are served from `GET /api/plugins/dashboard/cards`.

| Hook | Returns | Description |
|------|---------|-------------|
| `widget_get_cards()` | `list[dict] or None` | Widget card definitions |

Each card: `{id, title, value, subtitle, icon, link}` - `icon` is an mdi name
(e.g. `"mdi-controller"`), `link` an in-app path (e.g. `"/x/my-page"`).

```python
@hookimpl
def widget_get_cards(self):
    return [{
        "id": "my-stat", "title": "My Plugin", "value": "42",
        "subtitle": "things tracked", "icon": "mdi-chart-box", "link": "/x/my-page",
    }]
```
