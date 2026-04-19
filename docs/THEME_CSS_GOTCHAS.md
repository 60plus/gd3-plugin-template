# Theme Plugin: CSS Gotchas & Best Practices

Quick reference for the CSS patterns that catch theme plugin authors off guard, and the design tokens the core app exposes so your theme follows the user's active skin.

---

## 1. `mix-blend-mode` without `isolation: isolate` — the silent killer

### The bug

Fancy theme effects often use blend modes:

```css
.my-neon-grid  { position: fixed; mix-blend-mode: screen;   }  /* adds light */
.my-scanlines  { position: fixed; mix-blend-mode: multiply; }  /* adds shadow */
```

Without precaution these blend against **everything behind them in the root stacking context** — hero backgrounds, covers, dialogs, the full app. The classic symptom:

> *"Every hero image suddenly has a milky white fog on it"*

That is the neon grid's `screen` blend leaking through the entire DOM.

### The fix

Add `isolation: isolate` to the **root wrapper of your theme** (the element that contains the blend-mode children):

```css
.my-theme-shell {
  position: relative;          /* or fixed/absolute - needs stacking context */
  isolation: isolate;          /* <- THE IMPORTANT LINE */
}
```

`isolation: isolate` creates a new stacking context at that wrapper. Descendants with `mix-blend-mode` now blend only against content **inside** the wrapper, not against the viewport root.

### Real-world reference

NEON HORIZON plugin shipped this bug in versions `1.0.0 .. 1.3.0`. Fixed in `1.3.1` by adding `isolation: isolate` to `.nh-shell` (main layout) and `.cp` (couch layout). The GamesDownloader V3 core hit the identical bug in its own `AmbientBackground.vue` — session 31 in the project memo.

**Rule of thumb:** if your CSS contains `mix-blend-mode:` anywhere, the nearest positioned ancestor must have `isolation: isolate`.

---

## 2. Use core design tokens, don't hardcode

The core app exposes a full token system on `:root` (see [core docs/design-system.md](https://github.com/60plus/GamesDownloader/blob/main/docs/design-system.md)). Your theme inherits these automatically — use them instead of hardcoded pixels so your theme adapts when the user changes skins, sizes, or accessibility settings.

### Radius scale

```css
border-radius: var(--radius-xs, 4px);    /* chips, badges */
border-radius: var(--radius-sm, 8px);    /* inputs, small cards */
border-radius: var(--radius, 12px);      /* cards, dialogs */
border-radius: var(--radius-lg, 18px);   /* hero cards */
border-radius: var(--radius-pill, 999px);/* pills */
```

### Typography scale

```css
font-size: var(--fs-xs, 10px);   /* tiny labels */
font-size: var(--fs-sm, 12px);   /* body, quickfacts */
font-size: var(--fs-md, 14px);   /* default UI */
font-size: var(--fs-lg, 16px);   /* prominent labels */
font-size: var(--fs-xl, 18px);   /* subheads */
font-size: var(--fs-2xl, 22px);  /* page titles */
font-size: var(--fs-3xl, 28px);  /* hero titles */
```

### Spacing scale (4px base grid)

```css
padding: var(--space-2, 8px);    /* button padding */
padding: var(--space-4, 16px);   /* section padding */
gap:     var(--space-3, 12px);   /* card gap */
margin:  var(--space-6, 24px);   /* between sections */
```

Available: `--space-0 .. --space-12` (0, 4, 8, 12, 16, 20, 24, 32, 40, 48 px).

### Skin colours (override per-user)

```css
background: var(--bg);           /* primary bg */
color:      var(--text);         /* primary text */
color:      var(--muted);        /* secondary text */
accent:     var(--pl);           /* primary accent (skin hue) */
            var(--pl-light);     /* lighter variant */
            var(--pl-dim);       /* 12% tint */
            var(--pglow);        /* 50% glow tint */
border:     1px solid var(--border);
```

### Glass panel recipe

```css
.my-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur-px, 22px)) saturate(var(--glass-sat, 180%));
  -webkit-backdrop-filter: blur(var(--glass-blur-px, 22px)) saturate(var(--glass-sat, 180%));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
}
```

### Motion

```css
transition: background var(--transition, 0.16s ease);
transition: opacity    var(--transition-slow, 0.32s ease);
```

### Fallbacks matter

Always include a pixel fallback after the comma: `var(--fs-md, 14px)`. If your plugin loads in a weird edge case before skins.css is parsed, the fallback saves you from broken-looking UI. The core's own mechanical sweeps always preserve fallbacks.

---

## 3. `[data-animations="false"]` — respect the user's kill-switch

The core exposes a global kill-switch for all animations (Settings → Appearance → Animations toggle). Respect it:

```css
.my-animated-thing {
  animation: my-keyframes 3s ease-in-out infinite;
}

[data-animations="false"] .my-animated-thing {
  animation: none;
}
```

Users who get motion-sick or who simply want performance matter. Always pair your `animation:` declarations with an opt-out rule.

---

## 4. Respect `--hero-anim-speed` for synced animations

If your theme reuses the `kenburns` / `drift` / `pulse` naming for hero-like backgrounds, divide by the speed var so the user's *slow/normal/fast* Setting applies:

```css
.my-hero-bg--kenburns {
  animation: my-kenburns calc(44s / max(var(--hero-anim-speed, 1), 0.1)) ease-in-out infinite;
}
```

`max(..., 0.1)` guards against `0` (would divide to infinity).

---

## 5. Focus rings — inherited, don't override

Core ships a global `:focus-visible` ring:

```css
/* core base.css */
:focus-visible {
  outline: 2px solid var(--pl) !important;
  outline-offset: 2px !important;
  border-radius: inherit;
}
```

It's `!important` on purpose — to defeat scattered `outline: none` in legacy scoped styles. **Do not add `outline: none` to your interactive elements.** If you need a custom focus ring for a specific element, override with higher specificity + `:focus-visible`, not just `:focus`:

```css
/* good */
.my-fancy-button:focus-visible {
  outline: 3px solid var(--pl-light) !important;
  outline-offset: 3px !important;
}

/* bad - breaks keyboard a11y */
.my-fancy-button:focus { outline: none; }
```

---

## 6. Scoped Vue CSS and the `:global()` escape hatch

Vue SFC `<style scoped>` rewrites selectors to include a `[data-v-xxxxxx]` attribute, which means global pseudo-classes like `[data-animations="false"]` or `[data-skin="..."]` get auto-scoped and stop matching.

Escape with `:global()`:

```css
<style scoped>
.my-thing--kenburns { animation: my-kenburns 44s ease-in-out infinite; }

:global([data-animations="false"]) .my-thing--kenburns { animation: none; }
</style>
```

This tells Vue "don't scope the first selector, scope only the descendant".

---

## 7. `position: fixed` is not enough to contain blend modes

A common misconception:

> *"My overlay is `position: fixed; z-index: 9999` — it's isolated, right?"*

**Wrong.** `position: fixed` creates its own stacking context, but `mix-blend-mode` still reaches the **root** backdrop. Only `isolation: isolate` (or filter/transform/opacity < 1) on an ancestor creates a true blend boundary.

See #1.

---

## Quick checklist before shipping a theme plugin

- [ ] Every element with `mix-blend-mode` has an ancestor with `isolation: isolate`
- [ ] No `outline: none` on `:focus` or `:focus-visible`
- [ ] Radii use `--radius-*` tokens with fallbacks
- [ ] Font sizes use `--fs-*` tokens with fallbacks
- [ ] Paddings/margins/gaps use `--space-*` tokens with fallbacks
- [ ] Colours pull from `--pl`, `--bg`, `--muted`, `--text`, `--glass-*` — not hardcoded hexes
- [ ] `[data-animations="false"]` kill-switch respected (wrap in `:global()` inside scoped styles)
- [ ] Hero-like animations divide by `--hero-anim-speed`
- [ ] Visual test against at least 3 skins (Dark Purple / Deep Blue / Crimson Red) to catch hardcoded values
- [ ] Visual test with *Animations* toggle OFF

---

## See also

- Core design system: https://github.com/60plus/GamesDownloader/blob/main/docs/design-system.md
- Plugin hooks reference: [HOOKS.md](./HOOKS.md)
- NEON HORIZON example (real-world theme plugin): https://github.com/60plus/gd3-plugin-template
