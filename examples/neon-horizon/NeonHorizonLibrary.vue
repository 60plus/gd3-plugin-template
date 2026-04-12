<template>
  <div class="nh-lib">

    <!-- ── Toolbar (no search - navbar nh-search handles it) ──────────── -->
    <div class="nh-lib-toolbar">
      <div class="nh-lib-toolbar-left">
        <span class="nh-lib-count">{{ totalLabel }}</span>
      </div>
      <div class="nh-lib-toolbar-right">
        <select v-model="sortBy" class="nh-lib-select">
          <option v-for="o in sortOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
        <div class="nh-lib-sizes">
          <button v-for="s in sizes" :key="s.id" class="nh-lib-size-btn" :class="{ active: coverSize === s.id }" @click="setCoverSize(s.id)">{{ s.label }}</button>
        </div>
      </div>
    </div>

    <!-- ── Platform Strip (ONLY when inside a platform viewing ROMs) ────── -->
    <div v-if="libType === 'emulation' && platforms.length > 0" class="nh-plat-strip">
      <button
        v-for="p in platforms" :key="p.slug"
        class="nh-plat-pill" :class="{ active: activePlatform === p.slug }"
        @click="selectPlatform(p)"
      >
        <img :src="'/platforms/icons/' + p.fs_slug + '.png'" class="nh-plat-pill-icon" alt="" @error="hideImg" />
        <span>{{ p.name }}</span>
        <span class="nh-plat-pill-count">{{ p.rom_count }}</span>
      </button>
    </div>

    <!-- ── Empty State ──────────────────────────────────────────────────── -->
    <div v-if="!loading && filteredItems.length === 0" class="nh-lib-empty">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity=".3"><rect x="2" y="7" width="20" height="15" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>
      <div class="nh-lib-empty-text">{{ t('nh.no_games') }}</div>
    </div>

    <!-- ── Grid + Alphabet Sidebar ─────────────────────────────────────── -->
    <div v-if="libType !== 'emulation-home' && filteredItems.length > 0" class="nh-lib-body">

    <!-- Alphabet sticky right -->
    <div v-if="alphabetLetters.length > 0" class="nh-alpha">
      <button
        v-for="l in alphabetLetters" :key="l.letter"
        class="nh-alpha-btn"
        :class="{ available: l.available, active: l.letter === activeLetter }"
        @click="l.available && scrollToLetter(l.letter)"
      >{{ l.letter }}</button>
    </div>

    <!-- Big Picture Game Grid -->
    <div
      class="nh-bp-grid"
      :style="{ '--nh-bp-min': bpMinPx }"
      ref="gridRef"
    >
      <div
        v-for="item in filteredItems" :key="item.id"
        class="nh-bp-card"
        :class="{ 'nh-bp-no-lift': !themeStore.cardLift, 'nh-bp-no-glow': !themeStore.cardGlow, 'nh-bp-no-zoom': !themeStore.cardZoom }"
        :data-letter="itemFirstLetter(item)"
        @click="openItem(item)"
      >
        <div class="nh-bp-bg">
          <img v-if="itemBackground(item) || itemCover(item)" :src="itemBackground(item) || itemCover(item)" class="nh-bp-bg-img" loading="lazy" alt="" />
          <div v-else class="nh-bp-bg-fallback" />
        </div>
        <div class="nh-bp-gradient" />
        <img v-if="itemThumb(item)" :src="itemThumb(item)" class="nh-bp-thumb" loading="lazy" alt="" />
        <div v-if="itemRating(item)" class="nh-bp-rating">{{ itemRating(item) }}</div>
        <div v-if="itemBadge(item)" class="nh-bp-badge-dl">✓</div>
        <div class="nh-bp-info">
          <div class="nh-bp-title">{{ itemTitle(item) }}</div>
          <div v-if="itemMeta(item)" class="nh-bp-meta">{{ itemMeta(item) }}</div>
          <div v-if="itemGenres(item) && coverSize !== 's' && coverSize !== 'm'" class="nh-bp-genres">
            <span v-for="g in itemGenres(item).slice(0, 3)" :key="g" class="nh-bp-genre">{{ g }}</span>
          </div>
        </div>
      </div>
    </div>

    </div><!-- /nh-lib-body -->

    <!-- ── Platform Grid (emulation home) - Big cinematic cards ─────────── -->
    <div
      v-if="libType === 'emulation-home' && filteredItems.length > 0"
      class="nh-bp-grid"
      :style="{ '--nh-bp-min': bpMinPx }"
    >
      <div v-for="p in filteredItems" :key="p.id" class="nh-bp-card nh-bp-card--plat" @click="selectPlatform(p)">
        <div class="nh-bp-bg">
          <img :src="'/platforms/fanart/' + p.fs_slug + '.webp'" class="nh-bp-bg-img" alt="" loading="lazy" @error="(e:any) => e.target.src = '/platforms/fanart/_default.webp'" />
        </div>
        <div class="nh-bp-gradient nh-bp-gradient--plat" />
        <div class="nh-bp-plat-center">
          <img :src="'/platforms/icons/' + p.fs_slug + '.png'" class="nh-bp-plat-icon" alt="" @error="hideImg" />
        </div>
        <div class="nh-bp-info nh-bp-info--plat">
          <img :src="'/platforms/names/' + p.fs_slug + '.svg'" class="nh-bp-plat-logo" alt="" @error="onPlatLogoError" />
          <div v-if="platLogoFail[p.fs_slug]" class="nh-bp-plat-name-text">{{ p.name }}</div>
          <div class="nh-bp-plat-count">{{ t('nh.roms_count', { count: p.rom_count }) }}</div>
        </div>
      </div>
    </div>

    <!-- ── Pagination ───────────────────────────────────────────────────── -->
    <div v-if="totalPages > 1" class="nh-lib-pager">
      <button class="nh-lib-pager-btn" :disabled="page <= 1" @click="page--">◀</button>
      <span class="nh-lib-pager-info">{{ page }} / {{ totalPages }}</span>
      <button class="nh-lib-pager-btn" :disabled="page >= totalPages" @click="page++">▶</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const _gd = (window as any).__GD__
const client = _gd.api
const t = _gd.i18n?.t || ((k: string) => k)
const auth = _gd.stores.auth()
const router = useRouter()
const route = useRoute()

interface Platform { id: number; slug: string; fs_slug: string; name: string; rom_count: number; cover_aspect: string }

const themeStore = _gd.stores.theme()

const loading = ref(true)
const items = ref<any[]>([])
const platforms = ref<Platform[]>([])
const totalItems = ref(0)
const sortBy = ref('title')

// Search comes from navbar nh-search via route.query.q
const searchQuery = computed(() => {
  const q = route.query.q
  return (Array.isArray(q) ? q[0] : q) || ''
})
// Use theme store's coverSize (synced with Settings > Appearance)
const coverSize = computed(() => themeStore.coverSize || 'm')
const page = ref(1)
const perPage = 48
const gridRef = ref<HTMLElement | null>(null)
const activeLetter = ref('')
const platLogoFail = ref<Record<string, boolean>>({})

const isAdmin = computed(() => auth.user?.role === 'admin')

/* ── Route-based type ───────────────────────────────────────────────────── */
const libType = computed<'gog' | 'games' | 'emulation-home' | 'emulation'>(() => {
  const p = route.path
  if (p === '/library' || (p.startsWith('/library') && !p.match(/^\/library\/\d/))) return 'gog'
  if (p === '/games' || (p.startsWith('/games') && !p.match(/^\/games\/\d/))) return 'games'
  if (p === '/emulation') return 'emulation-home'
  if (p.startsWith('/emulation/') && !p.match(/^\/emulation\/[^/]+\/\d/)) return 'emulation'
  return 'games'
})

const activePlatform = computed(() => libType.value === 'emulation' ? (route.params.platform as string || '') : '')

// Reset sortBy when library type changes (emulation uses name_asc, others use title)
watch(libType, (t) => {
  if (t === 'emulation-home' || t === 'emulation') sortBy.value = 'name_asc'
  else sortBy.value = 'title'
}, { immediate: true })

/* ── Sort options ───────────────────────────────────────────────────────── */
const sortOptions = computed(() => {
  if (libType.value === 'emulation-home') return [
    { value: 'name_asc', label: t('nh.sort_az') }, { value: 'name_desc', label: t('nh.sort_za') },
    { value: 'roms_desc', label: t('nh.sort_most_roms') }, { value: 'roms_asc', label: t('nh.sort_fewest') },
  ]
  if (libType.value === 'emulation') return [
    { value: 'name_asc', label: t('nh.sort_az') }, { value: 'name_desc', label: t('nh.sort_za') },
    { value: 'year_desc', label: t('nh.sort_newest') }, { value: 'year_asc', label: t('nh.sort_oldest') },
  ]
  return [
    { value: 'title', label: t('nh.sort_az') }, { value: 'title_desc', label: t('nh.sort_za') },
    { value: 'rating', label: t('nh.sort_top_rated') }, { value: 'release', label: t('nh.sort_newest') },
  ]
})

const searchPlaceholder = computed(() => {
  const m: Record<string, string> = { gog: 'Search GOG…', games: 'Search games…', 'emulation-home': 'Search platforms…', emulation: 'Search ROMs…' }
  return m[libType.value] || 'Search…'
})

/* ── Sizes - persist to localStorage ────────────────────────────────────── */
const sizes = [
  { id: 's', label: 'S', min: 240 },
  { id: 'm', label: 'M', min: 320 },
  { id: 'l', label: 'L', min: 420 },
  { id: 'xl', label: 'XL', min: 520 },
]
const bpMinPx = computed(() => (sizes.find(s => s.id === coverSize.value)?.min || 320) + 'px')

function setCoverSize(id: string) {
  themeStore.setCoverSize(id)
}

/* ── Filtering + sorting ────────────────────────────────────────────────── */
const filteredItems = computed(() => {
  let arr = [...items.value]
  const q = searchQuery.value.toLowerCase().trim()

  if (libType.value === 'emulation-home') {
    if (q) arr = arr.filter((p: any) => p.name.toLowerCase().includes(q))
    const s = sortBy.value
    arr.sort((a: any, b: any) => {
      if (s === 'name_asc') return a.name.localeCompare(b.name)
      if (s === 'name_desc') return b.name.localeCompare(a.name)
      if (s === 'roms_desc') return b.rom_count - a.rom_count
      if (s === 'roms_asc') return a.rom_count - b.rom_count
      return 0
    })
    return arr
  }
  if (libType.value === 'gog' || libType.value === 'games') {
    if (q) arr = arr.filter((g: any) => (g.title || '').toLowerCase().includes(q))
    const s = sortBy.value
    arr.sort((a: any, b: any) => {
      if (s === 'title') return (a.title || '').localeCompare(b.title || '')
      if (s === 'title_desc') return (b.title || '').localeCompare(a.title || '')
      if (s === 'rating') return (b.rating || 0) - (a.rating || 0)
      if (s === 'release') return b.id - a.id
      return 0
    })
    return arr
  }
  return arr
})

const totalPages = computed(() => Math.ceil(totalItems.value / perPage))
const totalLabel = computed(() => {
  if (libType.value === 'emulation-home') return t('nh.platforms_count', { count: filteredItems.value.length })
  if (libType.value === 'emulation') return t('nh.roms_count', { count: totalItems.value })
  return t('nh.games_count', { count: filteredItems.value.length })
})

/* ── Alphabet quick nav ─────────────────────────────────────────────────── */
const ALL_LETTERS = '#ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

const alphabetLetters = computed(() => {
  const available = new Set<string>()
  for (const item of filteredItems.value) {
    const t = itemTitle(item)
    if (!t) continue
    const first = t[0].toUpperCase()
    available.add(/[A-Z]/.test(first) ? first : '#')
  }
  return ALL_LETTERS.map(l => ({ letter: l, available: available.has(l) }))
})

function itemFirstLetter(item: any): string {
  const t = itemTitle(item)
  if (!t) return '#'
  const first = t[0].toUpperCase()
  return /[A-Z]/.test(first) ? first : '#'
}

function scrollToLetter(letter: string) {
  activeLetter.value = letter
  if (!gridRef.value) return
  const card = gridRef.value.querySelector(`[data-letter="${letter}"]`) as HTMLElement
  if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' })
  setTimeout(() => { activeLetter.value = '' }, 1500)
}

/* ── Data fetching ──────────────────────────────────────────────────────── */
async function fetchData() {
  loading.value = true
  try {
    if (libType.value === 'gog') {
      const res = await client.get('/gog/library/games')
      const raw = res.data
      items.value = Array.isArray(raw) ? raw : raw.items ?? []
      totalItems.value = items.value.length
    } else if (libType.value === 'games') {
      const res = await client.get('/library/games', { params: { limit: '2000' } })
      items.value = res.data.items ?? []
      totalItems.value = items.value.length
    } else if (libType.value === 'emulation-home') {
      const res = await client.get('/roms/platforms')
      const plats = (Array.isArray(res.data) ? res.data : []).filter((p: Platform) => p.rom_count > 0)
      items.value = plats
      platforms.value = plats
      totalItems.value = plats.length
    } else if (libType.value === 'emulation') {
      const slug = route.params.platform as string
      const res = await client.get('/roms', {
        params: { platform_slug: slug, sort: sortBy.value, limit: perPage, offset: (page.value - 1) * perPage, search: searchQuery.value || undefined }
      })
      items.value = res.data.items ?? []
      totalItems.value = res.data.total ?? 0
      if (platforms.value.length === 0) {
        const pRes = await client.get('/roms/platforms')
        platforms.value = (Array.isArray(pRes.data) ? pRes.data : []).filter((p: Platform) => p.rom_count > 0)
      }
    }
  } catch (e) { console.error('[NH Library] fetch error:', e) }
  loading.value = false
}

/* ── Item helpers ────────────────────────────────────────────────────────── */
const _GOG_RE = /(_product_card|_logo2x?|_icon|_square_icon|_196|_200|_bg_crop_\d+x\d+)(\.\w+)?$/i
function gogCover(g: any): string {
  if (g.cover_path) return g.cover_path
  const url = g.cover_url || ''
  if (!url) return ''
  const fixed = url.replace(_GOG_RE, '')
  return /\.\w{2,5}(\?|$)/.test(fixed) ? fixed : fixed + '.jpg'
}
function itemCover(item: any): string { return libType.value === 'gog' ? gogCover(item) : (item.cover_path || '') }
function itemBackground(item: any): string { return item.background_path || '' }
function itemThumb(item: any): string {
  const cover = itemCover(item)
  if (!cover) return ''
  const bg = itemBackground(item)
  // No background → cover is used as card bg, skip thumb to avoid duplicate
  if (!bg) return ''
  if (cover !== bg) return cover
  // cover === background - try cover_url (original GOG cover)
  if (item.cover_url) return gogCover({ ...item, cover_path: null })
  return ''
}
function itemTitle(item: any): string { return (libType.value === 'emulation' || libType.value === 'emulation-home') ? (item.name || '') : (item.title || '') }
function itemRating(item: any): string {
  const r = item.rating
  if (!r || typeof r !== 'number') return ''
  return r.toFixed(1)
}
function itemMeta(item: any): string {
  const parts: string[] = []
  if (item.developer) parts.push(item.developer)
  if (item.release_year) parts.push(String(item.release_year))
  else if (item.release_date) { const y = item.release_date.slice(0, 4); if (y && y !== 'null') parts.push(y) }
  return parts.join(' · ')
}
function itemGenres(item: any): string[] | null { return item.genres?.length ? item.genres : null }
function itemBadge(item: any): boolean { return libType.value === 'gog' && item.is_downloaded }

/* ── Navigation ──────────────────────────────────────────────────────────── */
function openItem(item: any) {
  if (libType.value === 'gog') router.push({ name: 'game-detail', params: { id: item.id } })
  else if (libType.value === 'games') router.push({ name: 'games-detail', params: { id: item.id } })
  else if (libType.value === 'emulation') router.push({ name: 'emulation-detail', params: { platform: activePlatform.value, id: item.id } })
}
function selectPlatform(p: Platform) { router.push({ name: 'emulation-library', params: { platform: p.slug } }) }

function hideImg(e: Event) { (e.target as HTMLImageElement).style.display = 'none' }
function onPlatLogoError(e: Event) {
  const img = e.target as HTMLImageElement
  const m = img.src.match(/\/platforms\/names\/(.+)\.svg/)
  if (m) platLogoFail.value[m[1]] = true
  img.style.display = 'none'
}

/* ── Watchers ────────────────────────────────────────────────────────────── */
watch(() => route.path, () => { page.value = 1; fetchData() })
watch([sortBy, page], () => { if (libType.value === 'emulation') fetchData() })
let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchTimer) clearTimeout(searchTimer)
  if (libType.value === 'emulation') {
    searchTimer = setTimeout(() => { page.value = 1; fetchData() }, 300)
  }
})

onMounted(fetchData)
</script>

<style scoped>
/* Fonts loaded by theme system via plugin.py font field - no @import needed */

.nh-lib { display: flex; flex-direction: column; min-height: 100%; padding: 0 28px 48px; }

/* ═══ TOOLBAR ═══════════════════════════════════════════════════════════ */
.nh-lib-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 0; border-bottom: 1px solid var(--glass-border, rgba(0,212,255,.12)); margin-bottom: 16px; flex-wrap: wrap; }
.nh-lib-toolbar-left { display: flex; align-items: center; gap: 10px; }
.nh-lib-toolbar-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.nh-lib-select { background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 4px; color: var(--text); font-family: 'Rajdhani', sans-serif; font-size: 12px; font-weight: 600; padding: 6px 10px; cursor: pointer; outline: none; }
.nh-lib-select:focus { border-color: var(--pl); }
.nh-lib-select option { background: var(--bg2, #0a0a1a); color: var(--text); }

.nh-lib-sizes { display: flex; gap: 2px; }
.nh-lib-size-btn { padding: 5px 10px; border: 1px solid rgba(255,255,255,.08); border-radius: 3px; background: rgba(255,255,255,.03); color: var(--muted); font-family: 'Orbitron', sans-serif; font-size: 9px; font-weight: 700; cursor: pointer; transition: all .15s; }
.nh-lib-size-btn:hover { border-color: rgba(255,255,255,.2); color: var(--text); }
.nh-lib-size-btn.active { background: var(--pl-dim, rgba(0,212,255,.12)); border-color: var(--pl); color: var(--pl); box-shadow: 0 0 8px var(--pglow2); }

.nh-lib-count { font-family: 'Orbitron', sans-serif; font-size: 9px; font-weight: 700; color: var(--muted); letter-spacing: .08em; }

/* ═══ GRID + ALPHABET WRAPPER ═══════════════════════════════════════════ */
.nh-lib-body { display: flex; gap: 0; position: relative; }
.nh-lib-body .nh-bp-grid { flex: 1; min-width: 0; }

/* ═══ ALPHABET NAV - vertical sticky right ═════════════════════════════ */
.nh-alpha {
  position: sticky; top: 60px; align-self: flex-start;
  display: flex; flex-direction: column; gap: 1px;
  padding: 6px 4px; margin-left: 8px;
  background: rgba(5,5,15,.6); backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border, rgba(0,212,255,.08));
  border-radius: 4px; z-index: 5; order: 2;
}
.nh-alpha-btn {
  width: 22px; height: 18px; border: none; border-radius: 2px;
  background: none; color: rgba(255,255,255,.12);
  font-family: 'Orbitron', sans-serif; font-size: 8px; font-weight: 700;
  cursor: default; display: flex; align-items: center; justify-content: center;
  transition: all .12s; line-height: 1;
}
.nh-alpha-btn.available { color: var(--muted); cursor: pointer; }
.nh-alpha-btn.available:hover { color: var(--text); background: rgba(255,255,255,.08); }
.nh-alpha-btn.active { color: var(--pl) !important; background: var(--pl-dim, rgba(0,212,255,.15)); box-shadow: 0 0 6px var(--pglow2); }

/* ═══ PLATFORM STRIP ═══════════════════════════════════════════════════ */
.nh-plat-strip { display: flex; gap: 6px; overflow-x: auto; padding: 0 0 16px; scrollbar-width: none; }
.nh-plat-strip::-webkit-scrollbar { display: none; }
.nh-plat-pill { display: flex; align-items: center; gap: 6px; padding: 6px 14px; border: 1px solid rgba(255,255,255,.08); border-radius: 4px; background: rgba(255,255,255,.03); color: var(--muted); font-family: 'Rajdhani', sans-serif; font-size: 12px; font-weight: 700; white-space: nowrap; cursor: pointer; transition: all .2s; }
.nh-plat-pill:hover { color: var(--text); background: rgba(255,255,255,.06); }
.nh-plat-pill.active { color: var(--pl); background: var(--pl-dim, rgba(0,212,255,.1)); border-color: var(--pl); box-shadow: 0 0 10px var(--pglow2); }
.nh-plat-pill-icon { width: 16px; height: 16px; object-fit: contain; }
.nh-plat-pill-count { font-size: 10px; padding: 1px 6px; border-radius: 3px; background: rgba(255,255,255,.06); }
.nh-plat-pill.active .nh-plat-pill-count { background: var(--pl); color: #fff; }

/* ═══ BIG PICTURE GRID ═════════════════════════════════════════════════ */
.nh-bp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--nh-bp-min, 320px), 1fr)); gap: 16px; }

.nh-bp-card { position: relative; aspect-ratio: 16 / 9; border-radius: 6px; overflow: hidden; cursor: pointer; border: 1px solid rgba(255,255,255,.06); transition: all .35s cubic-bezier(.25,.46,.45,.94); }
.nh-bp-card:hover { transform: translateY(-6px) scale(1.02); border-color: var(--pl); box-shadow: 0 24px 60px rgba(0,0,0,.7), 0 0 30px var(--pglow2, rgba(0,212,255,.2)); z-index: 2; }

.nh-bp-bg { position: absolute; inset: -4px; }
.nh-bp-bg-img { width: calc(100% + 8px); height: calc(100% + 8px); object-fit: cover; filter: brightness(.55) saturate(1.2); transition: all .4s; }
.nh-bp-card:hover .nh-bp-bg-img { filter: brightness(.7) saturate(1.3); transform: scale(1.04); }
.nh-bp-bg-fallback { position: absolute; inset: 0; background: linear-gradient(135deg, var(--bg2, #0a0a1a), var(--bg3, #0f0f25)); }

.nh-bp-gradient { position: absolute; inset: 0; background: linear-gradient(180deg, transparent 0%, transparent 30%, rgba(5,5,15,.5) 60%, rgba(5,5,15,.92) 100%); z-index: 1; }
.nh-bp-gradient--plat { background: linear-gradient(180deg, rgba(5,5,15,.2) 0%, rgba(5,5,15,.4) 40%, rgba(5,5,15,.9) 100%); }

/* Thumb scales: XL=128x180, L=100x140, M=76x106, S=56x78 */
.nh-bp-thumb { position: absolute; top: calc(var(--nh-bp-min, 520px) * 0.019); left: calc(var(--nh-bp-min, 520px) * 0.019); max-width: calc(var(--nh-bp-min, 520px) * 0.246); max-height: calc(var(--nh-bp-min, 520px) * 0.346); width: auto; height: auto; object-fit: contain; border-radius: 4px; border: 1px solid rgba(255,255,255,.15); box-shadow: 0 4px 16px rgba(0,0,0,.6); z-index: 2; opacity: .85; transition: opacity .2s; }
.nh-bp-card:hover .nh-bp-thumb { opacity: 1; }

.nh-bp-rating { position: absolute; top: 10px; right: 10px; padding: 3px 10px; border-radius: 3px; background: rgba(0,0,0,.75); border: 1px solid var(--pl); font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 700; color: var(--pl); z-index: 2; box-shadow: 0 0 8px var(--pglow2); }

.nh-bp-badge-dl { position: absolute; bottom: 10px; right: 10px; width: 26px; height: 26px; border-radius: 50%; background: var(--ok, #22c55e); color: #fff; font-size: 13px; display: flex; align-items: center; justify-content: center; z-index: 2; box-shadow: 0 2px 8px rgba(0,0,0,.4); }

.nh-bp-info { position: absolute; bottom: 0; left: 0; right: 0; padding: 16px; z-index: 2; display: flex; flex-direction: column; gap: 4px; }
.nh-bp-info--plat { align-items: center; text-align: center; }

.nh-bp-title { font-family: 'Orbitron', sans-serif; font-size: 14px; font-weight: 900; color: #fff; text-shadow: 0 2px 8px rgba(0,0,0,.8); line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.nh-bp-meta { font-family: 'Rajdhani', sans-serif; font-size: 12px; color: rgba(255,255,255,.5); font-weight: 500; }
.nh-bp-genres { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 2px; }
.nh-bp-genre { padding: 2px 8px; border-radius: 3px; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1); font-size: 10px; font-weight: 600; color: rgba(255,255,255,.5); }

/* ═══ PLATFORM CARDS ═══════════════════════════════════════════════════ */
.nh-bp-plat-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -60%); z-index: 2; }
/* Icon, logo, count scale with --nh-bp-min (S=240 M=320 L=420 XL=520) */
.nh-bp-plat-icon { width: calc(var(--nh-bp-min, 320px) * 0.22); height: calc(var(--nh-bp-min, 320px) * 0.22); object-fit: contain; filter: drop-shadow(0 0 16px var(--pglow, rgba(0,212,255,.4))); transition: transform .3s; }
.nh-bp-card--plat:hover .nh-bp-plat-icon { transform: scale(1.15); }

.nh-bp-plat-logo { height: calc(var(--nh-bp-min, 320px) * 0.065); width: auto; max-width: 80%; object-fit: contain; filter: brightness(0) invert(1) drop-shadow(0 0 8px var(--pglow)); }
.nh-bp-plat-name-text { font-family: 'Orbitron', sans-serif; font-size: calc(var(--nh-bp-min, 320px) * 0.04); font-weight: 700; color: #fff; text-shadow: 0 0 8px var(--pglow); }
.nh-bp-plat-count { padding: calc(var(--nh-bp-min, 320px) * 0.012) calc(var(--nh-bp-min, 320px) * 0.04); border-radius: 4px; background: color-mix(in srgb, var(--pl, #00d4ff) 20%, transparent); backdrop-filter: blur(12px); border: 1px solid color-mix(in srgb, var(--pl, #00d4ff) 30%, transparent); font-family: 'Orbitron', sans-serif; font-size: calc(var(--nh-bp-min, 320px) * 0.03); font-weight: 700; color: var(--pl-light, #fff); letter-spacing: .04em; margin-top: calc(var(--nh-bp-min, 320px) * 0.02); }

/* ═══ CARD EFFECT TOGGLES ══════════════════════════════════════════════ */
.nh-bp-no-lift:hover { transform: none !important; }
.nh-bp-no-glow:hover { box-shadow: none !important; }
.nh-bp-no-zoom:hover .nh-bp-bg-img { transform: none !important; }

/* ═══ EMPTY + PAGER ════════════════════════════════════════════════════ */
.nh-lib-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; padding: 80px 20px; color: var(--muted); }
.nh-lib-empty-text { font-family: 'Orbitron', sans-serif; font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }

.nh-lib-pager { display: flex; align-items: center; justify-content: center; gap: 16px; padding: 28px 0 0; }
.nh-lib-pager-btn { padding: 6px 14px; border: 1px solid rgba(255,255,255,.1); border-radius: 4px; background: rgba(255,255,255,.04); color: var(--text); font-family: 'Rajdhani', sans-serif; font-size: 14px; font-weight: 700; cursor: pointer; transition: all .2s; }
.nh-lib-pager-btn:hover:not(:disabled) { border-color: var(--pl); box-shadow: 0 0 8px var(--pglow2); }
.nh-lib-pager-btn:disabled { opacity: .3; cursor: default; }
.nh-lib-pager-info { font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 700; color: var(--muted); letter-spacing: .06em; }

/* ═══ RESPONSIVE ═══════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .nh-lib { padding: 0 12px 32px; }
  .nh-bp-grid { gap: 10px; }
  .nh-bp-title { font-size: 12px; }
  .nh-alpha { display: none; }
}
</style>
