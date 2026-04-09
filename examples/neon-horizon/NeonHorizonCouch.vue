<template>
  <div class="ncouch" :style="rootStyle" @click.self="handleRootClick">

    <!-- ════════════════════════════════════════════════════════════════════
         SYSTEM VIEW — Colorful Pop style platform carousel
         ════════════════════════════════════════════════════════════════════ -->
    <template v-if="state === 'systems'">
      <!-- Background: platform fanart (blurred) -->
      <div class="nc-sys-bg">
        <transition name="nc-crossfade" mode="out-in">
          <img
            v-if="currentPlatform"
            :key="currentPlatform.fs_slug"
            :src="'/platforms/fanart/' + currentPlatform.fs_slug + '.webp'"
            class="nc-sys-bg-img"
            @error="(e:any) => e.target.style.opacity='0'"
          />
        </transition>
      </div>

      <!-- Color blocks (3 brightness variants of systemColor) -->
      <div class="nc-sys-color-block" :style="colorBlockStyle" />

      <!-- Left info panel -->
      <div class="nc-sys-info">
        <div class="nc-sys-year" :style="{ color: sysColor }">{{ currentPlatform?.release_year_platform || '' }}</div>
        <div class="nc-sys-name">{{ currentPlatform?.name || '' }}</div>
        <div class="nc-sys-desc">{{ currentPlatform?.description || '' }}</div>
        <div class="nc-sys-meta">
          <div class="nc-sys-logo-wrap">
            <img
              v-if="currentPlatform"
              :src="'/platforms/names/' + currentPlatform.fs_slug + '.svg'"
              class="nc-sys-logo"
              @error="(e:any) => e.target.style.display='none'"
            />
          </div>
          <div class="nc-sys-counts" :style="{ color: sysColor }">
            <span class="nc-sys-count-ico">🎮</span>
            <span>{{ currentPlatform?.rom_count || 0 }} games</span>
          </div>
        </div>
      </div>

      <!-- Vertical carousel (right side) -->
      <div class="nc-sys-carousel">
        <div
          v-for="(p, i) in visiblePlatforms"
          :key="p.fs_slug"
          class="nc-sys-card"
          :class="{ active: i === 1, prev: i === 0, next: i === 2 }"
          @click="i === 1 ? selectPlatform() : goSystem(i < 1 ? -1 : 1)"
        >
          <img
            :src="'/platforms/fanart/' + p.fs_slug + '.webp'"
            class="nc-sys-card-img"
            @error="(e:any) => e.target.style.opacity='0'"
          />
          <div class="nc-sys-card-overlay" />
          <div class="nc-sys-card-content">
            <img :src="'/platforms/icons/' + p.fs_slug + '.png'" class="nc-sys-card-icon" @error="(e:any) => e.target.style.display='none'" />
            <img :src="'/platforms/names/' + p.fs_slug + '.svg'" class="nc-sys-card-logo" @error="(e:any) => { e.target.style.display='none' }" />
            <div class="nc-sys-card-name">{{ p.name }}</div>
          </div>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="nc-sys-scroll-hint">▲▼</div>

      <!-- Bottom help bar -->
      <div class="nc-help">
        <span><kbd>←→</kbd> Navigate</span>
        <span><kbd>A</kbd> Select</span>
        <span><kbd>Start</kbd> Menu</span>
        <span><kbd>B</kbd> Exit</span>
      </div>
    </template>

    <!-- ════════════════════════════════════════════════════════════════════
         GAME LIST VIEW — detailed list + showcase
         ════════════════════════════════════════════════════════════════════ -->
    <template v-if="state === 'games-list'">
      <!-- Background panel -->
      <div class="nc-gl-bg" :style="{ backgroundColor: sysColorDim }" />

      <!-- Topbar -->
      <div class="nc-gl-topbar">
        <button class="nc-gl-back" @click="backToSystems">← Back</button>
        <div class="nc-gl-plat-pill" :style="{ borderColor: sysColor, color: sysColor }">
          <img :src="'/platforms/icons/' + currentPlatform?.fs_slug + '.png'" class="nc-gl-plat-icon" @error="(e:any) => e.target.style.display='none'" />
          {{ currentPlatform?.name }}
        </div>
        <div class="nc-gl-spacer" />
        <button class="nc-gl-view-btn" :class="{ active: gameView === 'list' }" @click="gameView = 'list'">☰</button>
        <button class="nc-gl-view-btn" :class="{ active: gameView === 'carousel' }" @click="gameView = 'carousel'">▦</button>
      </div>

      <!-- Game list (left) -->
      <div class="nc-gl-list" ref="gameListRef">
        <div
          v-for="(rom, i) in roms"
          :key="rom.id"
          class="nc-gl-item"
          :class="{ active: i === romIdx }"
          :style="i === romIdx ? { backgroundColor: sysColor } : {}"
          @click="romIdx = i"
        >
          <img v-if="rom.cover_path" :src="rom.cover_path" class="nc-gl-item-cover" />
          <div v-else class="nc-gl-item-cover nc-gl-item-cover--empty" />
          <span class="nc-gl-item-title">{{ rom.title }}</span>
        </div>
      </div>

      <!-- Showcase (right) -->
      <div class="nc-gl-showcase">
        <div class="nc-gl-cover-wrap">
          <img v-if="selectedRom?.cover_path" :src="selectedRom.cover_path" class="nc-gl-cover" />
          <div v-else class="nc-gl-cover nc-gl-cover--empty">No Cover</div>
        </div>
        <div class="nc-gl-detail">
          <img v-if="selectedRom?.wheel_path || detail?.wheel_path" :src="detail?.wheel_path || selectedRom?.wheel_path" class="nc-gl-wheel" @error="(e:any) => e.target.style.display='none'" />
          <div v-else class="nc-gl-title">{{ selectedRom?.title || '' }}</div>
          <div class="nc-gl-meta">
            <span v-if="selectedRom?.release_year">{{ selectedRom.release_year }}</span>
            <span v-if="detail?.genres?.length">{{ detail.genres.slice(0, 2).join(' · ') }}</span>
            <span v-if="detail?.developer">{{ detail.developer }}</span>
          </div>
          <div v-if="detail?.ss_score" class="nc-gl-rating" :style="{ color: sysColor }">
            {{ '★'.repeat(Math.round(detail.ss_score / 4)) }}{{ '☆'.repeat(5 - Math.round(detail.ss_score / 4)) }}
            <span class="nc-gl-rating-num">{{ (detail.ss_score / 2).toFixed(1) }}</span>
          </div>
          <div v-if="detail?.screenshots?.length" class="nc-gl-shots">
            <img
              v-for="(s, si) in detail.screenshots.slice(0, 4)"
              :key="si" :src="s"
              class="nc-gl-shot"
              @click="shotIdx = si"
            />
          </div>
          <div v-if="detail?.description" class="nc-gl-desc">{{ detail.description }}</div>
          <button class="nc-gl-play" :style="{ background: sysColor }" @click="launchGame">▶ PLAY</button>
        </div>
      </div>

      <div class="nc-help">
        <span><kbd>↑↓</kbd> Games</span>
        <span><kbd>A</kbd> Play</span>
        <span><kbd>X</kbd> Screenshots</span>
        <span><kbd>B</kbd> Back</span>
      </div>
    </template>

    <!-- ════════════════════════════════════════════════════════════════════
         GAME CAROUSEL VIEW — full-screen covers
         ════════════════════════════════════════════════════════════════════ -->
    <template v-if="state === 'games-carousel'">
      <!-- BG: selected game artwork -->
      <div class="nc-gc-bg">
        <img v-if="selectedRom?.background_path || selectedRom?.cover_path" :src="selectedRom.background_path || selectedRom.cover_path" class="nc-gc-bg-img" />
      </div>
      <div class="nc-gc-mask" />

      <div class="nc-gl-topbar">
        <button class="nc-gl-back" @click="backToSystems">← Back</button>
        <div class="nc-gl-plat-pill" :style="{ borderColor: sysColor, color: sysColor }">{{ currentPlatform?.name }}</div>
        <div class="nc-gl-spacer" />
        <button class="nc-gl-view-btn" :class="{ active: gameView === 'list' }" @click="gameView = 'list'">☰</button>
        <button class="nc-gl-view-btn" :class="{ active: gameView === 'carousel' }" @click="gameView = 'carousel'">▦</button>
      </div>

      <!-- Cover carousel -->
      <div class="nc-gc-track">
        <div
          v-for="(rom, i) in visibleRoms"
          :key="rom.id"
          class="nc-gc-card"
          :class="{ active: i === 2, side: i !== 2 }"
          @click="i === 2 ? launchGame() : (romIdx = romIdx + (i - 2))"
        >
          <img v-if="rom.cover_path" :src="rom.cover_path" class="nc-gc-card-img" />
          <div v-else class="nc-gc-card-img nc-gc-card--empty" />
        </div>
      </div>

      <!-- Game info overlay at bottom -->
      <div class="nc-gc-info">
        <div class="nc-gc-name">{{ selectedRom?.title || '' }}</div>
        <div class="nc-gc-meta">
          <span v-if="selectedRom?.release_year">{{ selectedRom.release_year }}</span>
          <span v-if="detail?.genres?.length">{{ detail.genres.slice(0, 2).join(' · ') }}</span>
          <span v-if="detail?.ss_score">★ {{ (detail.ss_score / 2).toFixed(1) }}</span>
        </div>
        <button class="nc-gc-play" :style="{ background: sysColor }" @click="launchGame">▶ PLAY</button>
      </div>

      <div class="nc-help">
        <span><kbd>←→</kbd> Games</span>
        <span><kbd>A</kbd> Play</span>
        <span><kbd>B</kbd> Back</span>
      </div>
    </template>

    <!-- ════════════════════════════════════════════════════════════════════
         OVERLAYS: Menu, Exit, Screenshot viewer
         ════════════════════════════════════════════════════════════════════ -->

    <!-- Menu -->
    <transition name="nc-fade">
      <div v-if="menuOpen" class="nc-overlay" @click.self="menuOpen = false">
        <div class="nc-menu">
          <div class="nc-menu-title" :style="{ color: sysColor }">SETTINGS</div>
          <div class="nc-menu-row" :class="{ focus: menuIdx === 0 }" @click="toggleView">
            View: {{ gameView === 'list' ? 'List' : 'Carousel' }}
          </div>
          <div class="nc-menu-row" :class="{ focus: menuIdx === 1 }" @click="cycleLaunchMode">
            Launch: {{ launchMode }}
          </div>
          <div class="nc-menu-row" :class="{ focus: menuIdx === 2 }" @click="toggleBezel">
            Bezel: {{ bezelOn ? 'ON' : 'OFF' }}
          </div>
          <div class="nc-menu-row nc-menu-row--resume" :class="{ focus: menuIdx === 3 }" @click="menuOpen = false">
            Resume
          </div>
          <div class="nc-menu-row nc-menu-row--exit" :class="{ focus: menuIdx === 4 }" @click="doExit">
            Exit Couch Mode
          </div>
          <div class="nc-menu-hint">↑↓ Navigate · A Select · B Close</div>
        </div>
      </div>
    </transition>

    <!-- Exit confirmation -->
    <transition name="nc-fade">
      <div v-if="exitOpen" class="nc-overlay" @click.self="exitOpen = false">
        <div class="nc-exit-panel">
          <div class="nc-exit-title">Exit Couch Mode?</div>
          <div class="nc-exit-row" :class="{ focus: exitIdx === 0 }" @click="exitOpen = false">Stay</div>
          <div class="nc-exit-row nc-exit-row--danger" :class="{ focus: exitIdx === 1 }" @click="doExit">Exit</div>
        </div>
      </div>
    </transition>

    <!-- Screenshot viewer -->
    <transition name="nc-fade">
      <div v-if="shotIdx >= 0 && detail?.screenshots" class="nc-overlay nc-shot-viewer" @click.self="shotIdx = -1">
        <img :src="detail.screenshots[shotIdx]" class="nc-shot-img" />
        <div class="nc-shot-counter">{{ shotIdx + 1 }} / {{ detail.screenshots.length }}</div>
      </div>
    </transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const _gd = (window as any).__GD__
const client = _gd.api
const auth = _gd.stores.auth()
const router = useRouter()

const { useCouchNav, couchNavPaused } = _gd.composables
const getEjsCore = _gd.getEjsCore

/* ── Types ──────────────────────────────────────────────────────────────── */
interface Platform {
  id: number; slug: string; fs_slug: string; name: string; rom_count: number
  cover_aspect: string | null; description: string | null; manufacturer: string | null
  release_year_platform: number | null; generation: number | null; wheel_path: string | null
}
interface Rom {
  id: number; slug: string; title: string; cover_path: string | null; cover_type: string | null
  cover_aspect: string | null; background_path: string | null; wheel_path: string | null
  video_path: string | null; release_year: number | null; bezel_path: string | null
}
interface RomDetail {
  description: string | null; screenshots: string[] | null; background_path: string | null
  developer: string | null; genres: string[] | null; ss_score: number | null
  video_path: string | null; wheel_path: string | null
  hltb_main_s: number | null; hltb_extra_s: number | null; hltb_complete_s: number | null
}

/* ── System colors per platform (from Colorful Pop) ─────────────────────── */
const PLATFORM_COLORS: Record<string, string> = {
  nes: '#c43d41', snes: '#df5142', n64: '#367d3f', gb: '#5a6e7e', gba: '#3f3f95',
  gbc: '#6b3fa0', nds: '#a0a0a0', genesis: '#c23b2c', megadrive: '#c23b2c',
  mastersystem: '#bf2020', gamegear: '#2c68b0', saturn: '#555555', dreamcast: '#e87d2a',
  psx: '#2555a0', psp: '#444444', neogeo: '#d4a935', arcade: '#e8b230',
  atarist: '#3a7bc8', atari2600: '#c85a30', atari7800: '#c85a30', atarilynx: '#bf4040',
  pce: '#e04040', pcengine: '#e04040', sega32x: '#2b2b9f',
  fbneo: '#e8b230', mame: '#e8b230',
}
const DEFAULT_SYS_COLOR = '#00d4ff'

/* ── State ──────────────────────────────────────────────────────────────── */
type ViewState = 'systems' | 'games-list' | 'games-carousel'
const state = ref<ViewState>('systems')
const platforms = ref<Platform[]>([])
const sysIdx = ref(0)
const roms = ref<Rom[]>([])
const romIdx = ref(0)
const detail = ref<RomDetail | null>(null)
const detailCache = new Map<number, RomDetail>()
const gameView = ref<'list' | 'carousel'>(localStorage.getItem('gd3_couch_view') as any || 'list')
const menuOpen = ref(false)
const menuIdx = ref(0)
const exitOpen = ref(false)
const exitIdx = ref(0)
const shotIdx = ref(-1)
const gameListRef = ref<HTMLElement | null>(null)
const loaded = new Set<string>()

const launchMode = ref(localStorage.getItem('gd3_couch_launch') || 'tab')
const bezelOn = ref(localStorage.getItem('gd3_couch_bezel') === 'on')

/* ── Computed ────────────────────────────────────────────────────────────── */
const currentPlatform = computed(() => platforms.value[sysIdx.value] ?? null)
const selectedRom = computed(() => roms.value[romIdx.value] ?? null)
const sysColor = computed(() => {
  const fs = currentPlatform.value?.fs_slug
  return fs ? (PLATFORM_COLORS[fs] || DEFAULT_SYS_COLOR) : DEFAULT_SYS_COLOR
})
const sysColorDim = computed(() => sysColor.value + '22')
const rootStyle = computed(() => ({ '--sys-color': sysColor.value }))
const colorBlockStyle = computed(() => ({ backgroundColor: sysColor.value, opacity: 0.15 }))

// Visible platforms for carousel (prev, current, next)
const visiblePlatforms = computed(() => {
  const arr = platforms.value
  if (arr.length === 0) return []
  const i = sysIdx.value
  const prev = arr[(i - 1 + arr.length) % arr.length]
  const cur = arr[i]
  const next = arr[(i + 1) % arr.length]
  return arr.length === 1 ? [cur] : arr.length === 2 ? [prev, cur] : [prev, cur, next]
})

// Visible ROMs for carousel (5 centered on current)
const visibleRoms = computed(() => {
  const arr = roms.value
  if (arr.length === 0) return []
  const result: Rom[] = []
  for (let d = -2; d <= 2; d++) {
    const idx = romIdx.value + d
    if (idx >= 0 && idx < arr.length) result.push(arr[idx])
    else result.push({ id: -1, slug: '', title: '', cover_path: null, cover_type: null, cover_aspect: null, background_path: null, wheel_path: null, video_path: null, release_year: null, bezel_path: null })
  }
  return result
})

/* ── Data fetching ──────────────────────────────────────────────────────── */
async function fetchPlatforms() {
  try {
    const { data } = await client.get('/roms/platforms')
    platforms.value = (Array.isArray(data) ? data : [])
      .filter((p: any) => p.rom_count > 0)
      .sort((a: any, b: any) => a.name.localeCompare(b.name))
      .map((p: any) => ({
        id: p.id, slug: p.slug, fs_slug: p.fs_slug,
        name: p.custom_name || p.name, rom_count: p.rom_count,
        cover_aspect: p.cover_aspect, description: null, manufacturer: null,
        release_year_platform: null, generation: null, wheel_path: null,
      }))
    if (platforms.value.length) loadPlatformDetail(sysIdx.value)
  } catch (e) { console.error('[NHCouch] fetch platforms:', e) }
}

async function loadPlatformDetail(idx: number) {
  for (let d = -1; d <= 1; d++) {
    const i = idx + d
    if (i < 0 || i >= platforms.value.length) continue
    const p = platforms.value[i]
    if (loaded.has(p.slug)) continue
    loaded.add(p.slug)
    try {
      const { data } = await client.get(`/roms/platforms/${p.slug}`)
      p.description = data.description ?? null
      p.manufacturer = data.manufacturer ?? null
      p.release_year_platform = data.release_year_platform ?? null
      p.generation = data.generation ?? null
      if (data.name_logo_path) p.wheel_path = data.name_logo_path
    } catch { /* silent */ }
  }
}

async function fetchRoms() {
  if (!currentPlatform.value) return
  try {
    const { data } = await client.get('/roms', {
      params: { platform_slug: currentPlatform.value.slug, limit: 500, offset: 0 }
    })
    const items = data.items ?? (Array.isArray(data) ? data : [])
    roms.value = items.map((r: any) => ({
      id: r.id, slug: r.slug, title: r.name || r.fs_name_no_ext,
      cover_path: r.cover_path, cover_type: r.cover_type, cover_aspect: r.cover_aspect,
      background_path: r.background_path, wheel_path: r.wheel_path,
      video_path: r.video_path, release_year: r.release_year, bezel_path: r.bezel_path,
    }))
    romIdx.value = 0
    detail.value = null
  } catch (e) { console.error('[NHCouch] fetch roms:', e) }
}

let detailTimer: ReturnType<typeof setTimeout> | null = null
async function loadRomDetail(rom: Rom) {
  if (detailCache.has(rom.id)) { detail.value = detailCache.get(rom.id)!; return }
  try {
    const { data } = await client.get(`/roms/${rom.id}`)
    const d: RomDetail = {
      description: data.summary ?? null, screenshots: data.screenshots ?? null,
      background_path: data.background_path ?? null, developer: data.developer ?? null,
      genres: data.genres ?? null, ss_score: data.ss_score ?? null,
      video_path: data.video_path ?? null, wheel_path: data.wheel_path ?? null,
      hltb_main_s: data.hltb_main_s ?? null, hltb_extra_s: data.hltb_extra_s ?? null,
      hltb_complete_s: data.hltb_complete_s ?? null,
    }
    detailCache.set(rom.id, d)
    if (selectedRom.value?.id === rom.id) detail.value = d
  } catch { /* silent */ }
}

/* ── Navigation ──────────────────────────────────────────────────────────── */
function goSystem(dir: number) {
  const next = sysIdx.value + dir
  if (next >= 0 && next < platforms.value.length) {
    sysIdx.value = next
    loadPlatformDetail(next)
  }
}

function selectPlatform() {
  state.value = gameView.value === 'list' ? 'games-list' : 'games-carousel'
  fetchRoms()
}

function backToSystems() {
  state.value = 'systems'
  roms.value = []
  detail.value = null
}

function launchGame() {
  const rom = selectedRom.value
  const plat = currentPlatform.value
  if (!rom || !plat) return
  const core = getEjsCore(plat.fs_slug)
  if (!core) return

  const params: Record<string, string> = {
    rom_id: String(rom.id), rom_name: rom.title, ejs_core: core, platform: plat.fs_slug,
  }
  if (bezelOn.value) params.bezel = '1'

  const url = '/player.html?' + new URLSearchParams(params).toString()
  const mode = launchMode.value
  if (mode === 'fullscreen') {
    window.location.href = url + '&returnTo=/couch'
  } else if (mode === 'window') {
    window.open(url, 'gd3-player', 'width=1280,height=720,menubar=no,toolbar=no')
  } else {
    window.open(url, '_blank')
  }
  couchNavPaused.value = true
  window.addEventListener('focus', () => { couchNavPaused.value = false }, { once: true })
}

function toggleView() { gameView.value = gameView.value === 'list' ? 'carousel' : 'list'; localStorage.setItem('gd3_couch_view', gameView.value) }
function cycleLaunchMode() {
  const modes = ['tab', 'window', 'fullscreen']
  const i = (modes.indexOf(launchMode.value) + 1) % modes.length
  launchMode.value = modes[i]
  localStorage.setItem('gd3_couch_launch', launchMode.value)
}
function toggleBezel() { bezelOn.value = !bezelOn.value; localStorage.setItem('gd3_couch_bezel', bezelOn.value ? 'on' : 'off') }
function doExit() { router.push('/') }
function handleRootClick() {}

/* ── Watchers ────────────────────────────────────────────────────────────── */
watch(sysIdx, () => loadPlatformDetail(sysIdx.value))
watch(romIdx, () => {
  detail.value = null
  shotIdx.value = -1
  if (detailTimer) clearTimeout(detailTimer)
  const rom = selectedRom.value
  if (rom) detailTimer = setTimeout(() => loadRomDetail(rom), 300)
  // Auto-scroll list
  nextTick(() => {
    const el = gameListRef.value?.querySelector('.nc-gl-item.active') as HTMLElement
    el?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  })
})
watch(gameView, (v) => {
  if (state.value.startsWith('games-')) state.value = v === 'list' ? 'games-list' : 'games-carousel'
})

/* ── Gamepad / keyboard nav ──────────────────────────────────────────────── */
useCouchNav({
  up: () => {
    if (menuOpen.value) { menuIdx.value = Math.max(0, menuIdx.value - 1); return }
    if (exitOpen.value) { exitIdx.value = 0; return }
    if (state.value === 'games-list' && romIdx.value > 0) romIdx.value--
  },
  down: () => {
    if (menuOpen.value) { menuIdx.value = Math.min(4, menuIdx.value + 1); return }
    if (exitOpen.value) { exitIdx.value = 1; return }
    if (state.value === 'games-list' && romIdx.value < roms.value.length - 1) romIdx.value++
  },
  left: () => {
    if (shotIdx.value > 0) { shotIdx.value--; return }
    if (state.value === 'systems') goSystem(-1)
    else if (state.value === 'games-carousel' && romIdx.value > 0) romIdx.value--
  },
  right: () => {
    if (shotIdx.value >= 0 && detail.value?.screenshots && shotIdx.value < detail.value.screenshots.length - 1) { shotIdx.value++; return }
    if (state.value === 'systems') goSystem(1)
    else if (state.value === 'games-carousel' && romIdx.value < roms.value.length - 1) romIdx.value++
  },
  confirm: () => {
    if (menuOpen.value) {
      [toggleView, cycleLaunchMode, toggleBezel, () => { menuOpen.value = false }, doExit][menuIdx.value]?.()
      return
    }
    if (exitOpen.value) { exitIdx.value === 1 ? doExit() : (exitOpen.value = false); return }
    if (state.value === 'systems') selectPlatform()
    else launchGame()
  },
  back: () => {
    if (shotIdx.value >= 0) { shotIdx.value = -1; return }
    if (menuOpen.value) { menuOpen.value = false; return }
    if (exitOpen.value) { exitOpen.value = false; return }
    if (state.value.startsWith('games-')) backToSystems()
    else exitOpen.value = true
  },
  menu: () => {
    if (exitOpen.value) return
    menuOpen.value = !menuOpen.value
    menuIdx.value = 0
  },
  x: () => {
    if (detail.value?.screenshots?.length && state.value.startsWith('games-')) shotIdx.value = 0
  },
})

onMounted(() => {
  document.documentElement.requestFullscreen?.().catch(() => {})
  fetchPlatforms()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

.ncouch {
  position: fixed; inset: 0; z-index: 9999;
  background: #050508; color: #fff;
  font-family: 'Rajdhani', sans-serif;
  overflow: hidden;
  user-select: none;
}

/* ═══ TRANSITIONS ═══════════════════════════════════════════════════════ */
.nc-crossfade-enter-active, .nc-crossfade-leave-active { transition: opacity .5s ease; }
.nc-crossfade-enter-from, .nc-crossfade-leave-to { opacity: 0; }
.nc-fade-enter-active, .nc-fade-leave-active { transition: opacity .2s ease; }
.nc-fade-enter-from, .nc-fade-leave-to { opacity: 0; }

/* ═══ SYSTEM VIEW ══════════════════════════════════════════════════════ */
.nc-sys-bg { position: absolute; inset: 0; z-index: 0; }
.nc-sys-bg-img { width: 100%; height: 100%; object-fit: cover; filter: blur(20px) brightness(.3) saturate(1.3); transition: opacity .5s; }

.nc-sys-color-block { position: absolute; left: 35.9%; top: 4.5%; width: 61.5%; height: 91%; z-index: 1; border-radius: 8px; }

.nc-sys-info { position: absolute; left: 2.6%; top: 4.5%; width: 30.7%; height: 91%; z-index: 10; display: flex; flex-direction: column; padding: 20px 0; }
.nc-sys-year { font-family: 'Orbitron', sans-serif; font-size: clamp(14px, 2.2vh, 22px); font-weight: 700; margin-top: 10%; letter-spacing: .05em; }
.nc-sys-name { font-family: 'Orbitron', sans-serif; font-size: clamp(22px, 4.5vh, 48px); font-weight: 900; color: #fff; margin-top: 2%; line-height: 1.1; text-shadow: 0 2px 12px rgba(0,0,0,.6); }
.nc-sys-desc { font-size: clamp(12px, 1.8vh, 16px); color: rgba(255,255,255,.55); line-height: 1.6; margin-top: 6%; max-height: 22vh; overflow-y: auto; scrollbar-width: none; }
.nc-sys-desc::-webkit-scrollbar { display: none; }

.nc-sys-meta { margin-top: auto; display: flex; flex-direction: column; gap: 10px; }
.nc-sys-logo-wrap { height: 50px; }
.nc-sys-logo { height: 100%; width: auto; max-width: 160px; object-fit: contain; filter: brightness(0) invert(1) drop-shadow(0 0 8px rgba(255,255,255,.3)); }
.nc-sys-counts { font-family: 'Orbitron', sans-serif; font-size: clamp(11px, 1.6vh, 15px); font-weight: 700; display: flex; align-items: center; gap: 8px; }
.nc-sys-count-ico { font-size: 1.2em; }

/* Carousel */
.nc-sys-carousel { position: absolute; right: 2%; top: 4.5%; width: 58%; height: 91%; z-index: 5; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; perspective: 1200px; }

.nc-sys-card { width: 55%; aspect-ratio: 3/4; border-radius: 12px; overflow: hidden; position: relative; cursor: pointer; transition: all .4s ease; border: 2px solid transparent; }
.nc-sys-card.active { border-color: var(--sys-color, #00d4ff); box-shadow: 0 0 40px color-mix(in srgb, var(--sys-color) 40%, transparent), 0 20px 60px rgba(0,0,0,.6); transform: scale(1); z-index: 3; }
.nc-sys-card.prev { transform: scale(.7) translateY(-30%) rotateX(8deg); opacity: .4; z-index: 1; }
.nc-sys-card.next { transform: scale(.7) translateY(30%) rotateX(-8deg); opacity: .4; z-index: 1; }

.nc-sys-card-img { width: 100%; height: 100%; object-fit: cover; }
.nc-sys-card-overlay { position: absolute; inset: 0; background: linear-gradient(180deg, transparent 40%, rgba(0,0,0,.8) 100%); }
.nc-sys-card-content { position: absolute; bottom: 0; left: 0; right: 0; padding: 16px; display: flex; flex-direction: column; align-items: center; gap: 6px; z-index: 2; }
.nc-sys-card-icon { width: 32px; height: 32px; object-fit: contain; filter: drop-shadow(0 0 6px rgba(255,255,255,.4)); }
.nc-sys-card-logo { height: 16px; width: auto; max-width: 120px; filter: brightness(0) invert(1); }
.nc-sys-card-name { font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 700; text-shadow: 0 1px 4px rgba(0,0,0,.8); }

.nc-sys-scroll-hint { position: absolute; right: 3%; bottom: 6%; z-index: 10; font-size: 20px; color: rgba(255,255,255,.25); animation: nc-bounce 2s ease-in-out infinite; }
@keyframes nc-bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }

/* ═══ GAME LIST VIEW ═══════════════════════════════════════════════════ */
.nc-gl-bg { position: absolute; left: 2.6%; top: 4.6%; width: 56.2%; height: 90.8%; z-index: 0; border-radius: 10px; }

.nc-gl-topbar { position: absolute; top: 0; left: 0; right: 0; height: 48px; z-index: 20; display: flex; align-items: center; gap: 12px; padding: 0 2.6%; }
.nc-gl-back { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); border-radius: 6px; color: #fff; font-family: 'Rajdhani'; font-size: 13px; font-weight: 700; padding: 6px 14px; cursor: pointer; }
.nc-gl-back:hover { background: rgba(255,255,255,.15); }
.nc-gl-plat-pill { display: flex; align-items: center; gap: 6px; padding: 4px 14px; border: 1px solid; border-radius: 20px; font-family: 'Orbitron'; font-size: 10px; font-weight: 700; letter-spacing: .06em; }
.nc-gl-plat-icon { width: 16px; height: 16px; object-fit: contain; }
.nc-gl-spacer { flex: 1; }
.nc-gl-view-btn { background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1); border-radius: 4px; color: rgba(255,255,255,.4); font-size: 16px; width: 32px; height: 32px; cursor: pointer; }
.nc-gl-view-btn.active { color: var(--sys-color); border-color: var(--sys-color); }

/* Left game list */
.nc-gl-list { position: absolute; left: 5.2%; top: 22.1%; width: 18.7%; height: 68.6%; z-index: 10; overflow-y: auto; scrollbar-width: none; display: flex; flex-direction: column; gap: 2px; }
.nc-gl-list::-webkit-scrollbar { display: none; }
.nc-gl-item { display: flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: background .15s; white-space: nowrap; overflow: hidden; }
.nc-gl-item.active { color: #fff; }
.nc-gl-item:not(.active) { color: rgba(255,255,255,.45); }
.nc-gl-item:not(.active):hover { background: rgba(255,255,255,.06); }
.nc-gl-item-cover { width: 36px; height: 48px; object-fit: cover; border-radius: 3px; flex-shrink: 0; }
.nc-gl-item-cover--empty { width: 36px; height: 48px; background: rgba(255,255,255,.06); border-radius: 3px; flex-shrink: 0; }
.nc-gl-item-title { font-size: 13px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; }

/* Right showcase */
.nc-gl-showcase { position: absolute; left: 26%; top: 10%; right: 2%; bottom: 8%; z-index: 10; display: flex; gap: 24px; }
.nc-gl-cover-wrap { flex-shrink: 0; width: 27.9%; display: flex; align-items: center; justify-content: center; }
.nc-gl-cover { max-width: 100%; max-height: 75vh; object-fit: contain; border-radius: 8px; border: 2px solid rgba(255,255,255,.1); box-shadow: 0 12px 40px rgba(0,0,0,.6); }
.nc-gl-cover--empty { width: 100%; aspect-ratio: 3/4; background: rgba(255,255,255,.04); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,.15); font-size: 14px; }

.nc-gl-detail { flex: 1; display: flex; flex-direction: column; gap: 10px; overflow-y: auto; scrollbar-width: none; padding-top: 12%; }
.nc-gl-detail::-webkit-scrollbar { display: none; }
.nc-gl-wheel { height: 40px; width: auto; max-width: 250px; object-fit: contain; filter: brightness(0) invert(1); }
.nc-gl-title { font-family: 'Orbitron'; font-size: clamp(18px, 3.5vh, 32px); font-weight: 900; line-height: 1.1; }
.nc-gl-meta { font-size: 13px; color: rgba(255,255,255,.45); display: flex; gap: 12px; flex-wrap: wrap; }
.nc-gl-rating { font-size: 16px; letter-spacing: 2px; }
.nc-gl-rating-num { font-family: 'Orbitron'; font-size: 14px; font-weight: 700; margin-left: 8px; }

.nc-gl-shots { display: flex; gap: 6px; margin-top: 4px; }
.nc-gl-shot { width: 80px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid rgba(255,255,255,.1); cursor: pointer; transition: border-color .2s; }
.nc-gl-shot:hover { border-color: var(--sys-color); }

.nc-gl-desc { font-size: 13px; color: rgba(255,255,255,.45); line-height: 1.6; max-height: 15vh; overflow-y: auto; scrollbar-width: none; }
.nc-gl-desc::-webkit-scrollbar { display: none; }

.nc-gl-play { align-self: flex-start; padding: 10px 32px; border: none; border-radius: 8px; color: #fff; font-family: 'Orbitron'; font-size: 14px; font-weight: 700; letter-spacing: .08em; cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,.4); transition: all .2s; margin-top: auto; }
.nc-gl-play:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,.5); }

/* ═══ GAME CAROUSEL VIEW ═══════════════════════════════════════════════ */
.nc-gc-bg { position: absolute; inset: 0; z-index: 0; }
.nc-gc-bg-img { width: 100%; height: 100%; object-fit: cover; filter: brightness(.25) saturate(1.2); }
.nc-gc-mask { position: absolute; inset: 0; z-index: 1; background: radial-gradient(ellipse at 50% 50%, transparent 30%, rgba(5,5,8,.85) 100%); }

.nc-gc-track { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -55%); z-index: 5; display: flex; align-items: center; gap: 16px; perspective: 1000px; }
.nc-gc-card { width: 160px; aspect-ratio: 3/4; border-radius: 8px; overflow: hidden; transition: all .3s ease; border: 2px solid transparent; flex-shrink: 0; }
.nc-gc-card.active { width: 240px; border-color: var(--sys-color); box-shadow: 0 0 30px color-mix(in srgb, var(--sys-color) 30%, transparent), 0 16px 48px rgba(0,0,0,.6); transform: scale(1); cursor: pointer; }
.nc-gc-card.side { opacity: .35; filter: blur(1px); transform: scale(.85); }
.nc-gc-card-img { width: 100%; height: 100%; object-fit: cover; }
.nc-gc-card--empty { width: 100%; height: 100%; background: rgba(255,255,255,.04); }

.nc-gc-info { position: absolute; bottom: 10%; left: 50%; transform: translateX(-50%); z-index: 10; text-align: center; max-width: 500px; }
.nc-gc-name { font-family: 'Orbitron'; font-size: clamp(20px, 3.5vh, 36px); font-weight: 900; text-shadow: 0 2px 12px rgba(0,0,0,.8); }
.nc-gc-meta { font-size: 13px; color: rgba(255,255,255,.45); display: flex; gap: 12px; justify-content: center; margin-top: 6px; }
.nc-gc-play { margin-top: 16px; padding: 10px 32px; border: none; border-radius: 8px; color: #fff; font-family: 'Orbitron'; font-size: 14px; font-weight: 700; letter-spacing: .08em; cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,.4); }

/* ═══ HELP BAR ═════════════════════════════════════════════════════════ */
.nc-help { position: absolute; bottom: 0; left: 0; right: 0; z-index: 20; padding: 8px 2.6%; display: flex; gap: 20px; font-size: 11px; color: rgba(255,255,255,.2); }
.nc-help kbd { background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.12); border-radius: 3px; padding: 1px 5px; font-size: 10px; font-family: inherit; color: rgba(255,255,255,.3); }

/* ═══ OVERLAYS ═════════════════════════════════════════════════════════ */
.nc-overlay { position: fixed; inset: 0; z-index: 200; background: rgba(0,0,0,.78); backdrop-filter: blur(12px); display: flex; align-items: center; justify-content: center; }

.nc-menu { width: 360px; background: rgba(10,6,24,.97); border: 1px solid rgba(255,255,255,.1); border-radius: 16px; padding: 24px 20px; display: flex; flex-direction: column; gap: 6px; }
.nc-menu-title { font-family: 'Orbitron'; font-size: 10px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 8px; }
.nc-menu-row { padding: 12px 16px; border-radius: 10px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.06); font-size: 14px; font-weight: 600; color: rgba(255,255,255,.6); cursor: pointer; transition: all .12s; }
.nc-menu-row.focus { background: rgba(255,255,255,.1); border-color: var(--sys-color, rgba(0,212,255,.35)); color: #fff; }
.nc-menu-row--exit { color: #ef4444; }
.nc-menu-row--exit.focus { background: rgba(239,68,68,.12); border-color: rgba(239,68,68,.35); }
.nc-menu-hint { text-align: center; margin-top: 8px; font-size: 10px; color: rgba(255,255,255,.2); }

.nc-exit-panel { width: 300px; background: rgba(10,6,24,.97); border: 1px solid rgba(255,255,255,.1); border-radius: 16px; padding: 24px 20px; text-align: center; }
.nc-exit-title { font-family: 'Orbitron'; font-size: 14px; font-weight: 700; margin-bottom: 16px; }
.nc-exit-row { padding: 12px; border-radius: 10px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.06); margin-bottom: 6px; cursor: pointer; font-weight: 600; }
.nc-exit-row.focus { background: rgba(255,255,255,.1); border-color: var(--sys-color); color: #fff; }
.nc-exit-row--danger.focus { background: rgba(239,68,68,.12); border-color: rgba(239,68,68,.35); color: #ef4444; }

.nc-shot-viewer { cursor: zoom-out; }
.nc-shot-img { max-width: 90vw; max-height: 85vh; object-fit: contain; border-radius: 8px; box-shadow: 0 16px 60px rgba(0,0,0,.8); }
.nc-shot-counter { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); font-family: 'Orbitron'; font-size: 12px; color: rgba(255,255,255,.4); }

/* ═══ RESPONSIVE ═══════════════════════════════════════════════════════ */
@media (max-width: 900px) {
  .nc-sys-info { width: 90%; left: 5%; top: auto; bottom: 5%; height: auto; }
  .nc-sys-carousel { width: 100%; right: 0; top: 5%; height: 50%; }
  .nc-gl-list { width: 30%; }
  .nc-gl-showcase { left: 35%; }
}
</style>
