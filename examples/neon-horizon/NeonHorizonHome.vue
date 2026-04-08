<template>
  <div class="nh-home">

    <!-- ── Hero Banner ────────────────────────────────────────────────── -->
    <section
      v-if="currentHero"
      class="nh-hero"
      @mouseenter="stopHeroRotation"
      @mouseleave="startHeroRotation"
    >
      <div class="nh-hero-bg" :class="{ 'nh-hero-bg--fade': heroFading, 'nh-hero-bg--no-anim': !themeStore.animations }">
        <img
          :src="currentHero.background || currentHero.cover || ''"
          :key="currentHero.id + '-' + currentHero.library"
          class="nh-hero-bg-img"
          alt=""
        />
      </div>
      <div class="nh-hero-gradient" />
      <div class="nh-hero-gradient-side" />

      <div class="nh-hero-content">
        <span class="nh-hero-badge">{{ heroLibraryLabel }}</span>
        <h1 class="nh-hero-title">{{ currentHero.title }}</h1>
        <div v-if="currentHero.genres?.length" class="nh-hero-genres">
          <span
            v-for="g in currentHero.genres.slice(0, 4)"
            :key="g"
            class="nh-hero-genre"
          >{{ g }}</span>
        </div>
        <div class="nh-hero-actions">
          <button class="nh-hero-btn nh-hero-btn--primary" @click="navigateToHero(currentHero)">
            View Details
          </button>
        </div>
      </div>

      <div v-if="heroPool.length > 1" class="nh-hero-dots">
        <button
          v-for="(_, i) in heroPool.slice(0, 10)"
          :key="i"
          class="nh-hero-dot"
          :class="{ active: i === heroIndex }"
          @click="jumpToHero(i)"
        />
      </div>
    </section>

    <!-- ── Recently Added — GOG ─────────────────────────────────────────── -->
    <section v-if="isAdmin && gogLib.recent.length" class="nh-recent">
      <div class="nh-section-head">
        <button class="nh-section-title nh-section-link" @click="router.push('/library')">
          Recently Added — GOG Library
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <div class="nh-row-nav">
          <button class="nh-nav-btn" @click="scrollRow('gog','left')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg></button>
          <button class="nh-nav-btn" @click="scrollRow('gog','right')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></button>
        </div>
      </div>
      <div class="nh-scroll" :ref="(el:any) => { if (el) rowRefs['gog'] = el }">
        <div v-for="g in gogLib.recent" :key="g.id" class="nh-cover-card" @click="openGogGame(g)">
          <div class="nh-cover-img-wrap">
            <img v-if="gogCoverSrc(g)" :src="gogCoverSrc(g)" class="nh-cover-img" loading="lazy" />
            <div v-else class="nh-cover-fallback" />
            <div class="nh-cover-overlay"><span class="nh-cover-title">{{ g.title }}</span></div>
          </div>
          <div class="nh-cover-label">{{ g.title }}</div>
        </div>
      </div>
    </section>

    <!-- ── Recently Added — Games Library ────────────────────────────────── -->
    <section v-if="customLib.recent.length" class="nh-recent">
      <div class="nh-section-head">
        <button class="nh-section-title nh-section-link" @click="router.push('/games')">
          Recently Added — Games Library
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <div class="nh-row-nav">
          <button class="nh-nav-btn" @click="scrollRow('custom','left')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg></button>
          <button class="nh-nav-btn" @click="scrollRow('custom','right')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></button>
        </div>
      </div>
      <div class="nh-scroll" :ref="(el:any) => { if (el) rowRefs['custom'] = el }">
        <div v-for="g in customLib.recent" :key="g.id" class="nh-cover-card" @click="openGame(g)">
          <div class="nh-cover-img-wrap">
            <img v-if="g.cover_path" :src="g.cover_path" class="nh-cover-img" loading="lazy" />
            <div v-else class="nh-cover-fallback" />
            <div class="nh-cover-overlay"><span class="nh-cover-title">{{ g.title }}</span></div>
          </div>
          <div class="nh-cover-label">{{ g.title }}</div>
        </div>
      </div>
    </section>

    <!-- ── Recently Added — Emulation ────────────────────────────────────── -->
    <section v-if="emuRecent.length" class="nh-recent">
      <div class="nh-section-head">
        <button class="nh-section-title nh-section-link" @click="router.push('/emulation')">
          Recently Added — Emulation Library
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <div class="nh-row-nav">
          <button class="nh-nav-btn" @click="scrollRow('emu','left')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg></button>
          <button class="nh-nav-btn" @click="scrollRow('emu','right')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></button>
        </div>
      </div>
      <div class="nh-scroll" :ref="(el:any) => { if (el) rowRefs['emu'] = el }">
        <div v-for="r in emuRecent" :key="r.id" class="nh-cover-card" @click="openEmuRom(r)">
          <div class="nh-cover-img-wrap" :style="{ aspectRatio: romAspect(r) }">
            <img v-if="r.cover_path" :src="r.cover_path" class="nh-cover-img" loading="lazy" />
            <div v-else class="nh-cover-fallback" />
            <div class="nh-cover-overlay"><span class="nh-cover-title">{{ r.name }}</span></div>
          </div>
          <div class="nh-cover-label">{{ r.name }}</div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

// Use GD plugin API for stores and API client
const _gd = (window as any).__GD__
const client = _gd.api

/* ── Interfaces ─────────────────────────────────────────────────────────── */
interface LibGame { id: number; title: string; slug: string; source: string; cover_path: string | null; background_path: string | null; genres?: string[] }
interface GogGame { id: number; title: string; slug: string; cover_path: string | null; cover_url: string | null; background_path: string | null; genres?: string[] }
interface EmuRom  { id: number; name: string; cover_path: string | null; cover_type: string | null; cover_aspect: string | null; background_path: string | null; platform_slug: string | null; platform_fs_slug: string | null; platform_name: string | null; platform_cover_aspect: string }

interface HeroGame {
  id: number
  title: string
  library: 'gog' | 'games' | 'emulation'
  cover: string | null
  background: string | null
  genres?: string[]
  platformSlug?: string
}

/* ── Helpers ─────────────────────────────────────────────────────────────── */
const _GOG_SUFFIX_RE = /(_product_card|_logo2x?|_icon|_square_icon|_196|_200|_bg_crop_\d+x\d+)(\.\w+)?$/i
function gogCoverSrc(g: GogGame): string {
  if (g.cover_path) return g.cover_path
  const url = g.cover_url || ''
  if (!url) return ''
  const fixed = url.replace(_GOG_SUFFIX_RE, '')
  return /\.\w{2,5}(\?|$)/.test(fixed) ? fixed : fixed + '.jpg'
}

const router = useRouter()
const auth   = _gd.stores.auth()
const themeStore = _gd.stores.theme()

/* ── State ───────────────────────────────────────────────────────────────── */
const libGames  = ref<LibGame[]>([])
const gogGames  = ref<GogGame[]>([])
const emuRecent = ref<EmuRom[]>([])
const rowRefs   = ref<Record<string, HTMLElement>>({})

const isAdmin = computed(() => auth.user?.role === 'admin')

/* ── Hero ────────────────────────────────────────────────────────────────── */
const heroPool    = ref<HeroGame[]>([])
const heroIndex   = ref(0)
const heroFading  = ref(false)
let heroTimer: ReturnType<typeof setInterval> | null = null

const currentHero = computed(() => heroPool.value[heroIndex.value] ?? null)

const heroLibraryLabel = computed(() => {
  if (!currentHero.value) return ''
  const m: Record<string, string> = { gog: 'GOG Library', games: 'Games Library', emulation: 'Emulation' }
  return m[currentHero.value.library] || ''
})

function buildHeroPool() {
  const pool: HeroGame[] = []
  for (const g of gogGames.value) {
    if (g.background_path) pool.push({ id: g.id, title: g.title, library: 'gog', cover: g.cover_path ?? gogCoverSrc(g), background: g.background_path, genres: g.genres })
  }
  for (const g of libGames.value) {
    if (g.background_path) pool.push({ id: g.id, title: g.title, library: 'games', cover: g.cover_path, background: g.background_path, genres: g.genres })
  }
  for (const r of emuRecent.value) {
    if (r.background_path || r.cover_path) pool.push({ id: r.id, title: r.name, library: 'emulation', cover: r.cover_path, background: r.background_path || r.cover_path, platformSlug: r.platform_slug ?? undefined })
  }
  // Shuffle
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]]
  }
  heroPool.value = pool.slice(0, 20)
  heroIndex.value = 0
}

function advanceHero() {
  if (heroPool.value.length < 2) return
  heroFading.value = true
  setTimeout(() => {
    heroIndex.value = (heroIndex.value + 1) % heroPool.value.length
    heroFading.value = false
  }, 600)
}

function startHeroRotation() {
  stopHeroRotation()
  if (heroPool.value.length > 1 && themeStore.heroAnim) heroTimer = setInterval(advanceHero, 10000)
}

function stopHeroRotation() {
  if (heroTimer) { clearInterval(heroTimer); heroTimer = null }
}

function jumpToHero(i: number) {
  if (i === heroIndex.value) return
  heroFading.value = true
  setTimeout(() => {
    heroIndex.value = i
    heroFading.value = false
  }, 600)
}

function navigateToHero(hero: HeroGame) {
  if (hero.library === 'gog') router.push({ name: 'game-detail', params: { id: hero.id } })
  else if (hero.library === 'games') router.push({ name: 'games-detail', params: { id: hero.id } })
  else if (hero.library === 'emulation' && hero.platformSlug) router.push({ name: 'emulation-detail', params: { platform: hero.platformSlug, id: hero.id } })
}

/* ── Library helpers ─────────────────────────────────────────────────────── */
function buildLib<T extends { id: number; cover_path?: string | null; background_path?: string | null }>(games: T[]) {
  return {
    count: games.length,
    recent: [...games].sort((a, b) => b.id - a.id).slice(0, 24) as (T & { title: string })[],
  }
}

const gogLib    = computed(() => buildLib(gogGames.value))
const customLib = computed(() => buildLib(libGames.value))

function romAspect(r: EmuRom): string { return r.cover_type === 'box-3D' ? '16/9' : (r.cover_aspect || r.platform_cover_aspect || '3/4') }

/* ── Fetch ───────────────────────────────────────────────────────────────── */
async function fetchAll() {
  const [recentRes, libRes, gogRes] = await Promise.allSettled([
    client.get('/roms/recent', { params: { limit: 24 } }),
    client.get('/library/games', { params: { limit: '24', offset: '0' } }),
    isAdmin.value ? client.get('/gog/library/games') : Promise.resolve({ data: [] }),
  ])
  if (recentRes.status === 'fulfilled') emuRecent.value = recentRes.value.data as EmuRom[]
  if (libRes.status === 'fulfilled')
    libGames.value = (libRes.value.data.items as any[]).map((g: any) => ({ id: g.id, title: g.title, slug: g.slug, source: g.source, cover_path: g.cover_path ?? null, background_path: g.background_path ?? null, genres: g.genres ?? [] }))
  if (gogRes.status === 'fulfilled') {
    const raw = gogRes.value.data
    gogGames.value = (Array.isArray(raw) ? raw : raw.items ?? []).map((g: any) => ({ id: g.id, title: g.title, slug: g.slug, cover_path: g.cover_path ?? null, cover_url: g.cover_url ?? null, background_path: g.background_path ?? null, genres: g.genres ?? [] }))
  }

  buildHeroPool()
  startHeroRotation()
}

/* ── Navigation ──────────────────────────────────────────────────────────── */
function openGame(g: LibGame) { router.push({ name: 'games-detail', params: { id: g.id } }) }
function openGogGame(g: GogGame) { router.push({ name: 'game-detail', params: { id: g.id } }) }
function openEmuRom(r: EmuRom) { if (r.platform_slug) router.push({ name: 'emulation-detail', params: { platform: r.platform_slug, id: r.id } }) }
function scrollRow(k: string, d: 'left'|'right') { rowRefs.value[k]?.scrollBy({ left: d === 'right' ? 420 : -420, behavior: 'smooth' }) }

onMounted(fetchAll)
onUnmounted(stopHeroRotation)
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   NEON HORIZON HOME — Netflix-style dashboard
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-home {
  display: flex; flex-direction: column;
  min-height: 100%;
}


/* ═══════════════════════════════════════════════════════════════════════════
   HERO BANNER
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-hero {
  position: relative;
  height: 420px;
  overflow: hidden;
  flex-shrink: 0;
}

.nh-hero-bg {
  position: absolute;
  inset: -10px;
  transition: opacity .6s ease;
}

.nh-hero-bg--fade {
  opacity: 0.3;
}

.nh-hero-bg-img {
  width: calc(100% + 20px);
  height: calc(100% + 20px);
  object-fit: cover;
  filter: brightness(.4) saturate(1.3);
  animation: nh-hero-drift 30s ease-in-out infinite alternate;
}

@keyframes nh-hero-drift {
  0%   { transform: scale(1.05) translate(0, 0); }
  100% { transform: scale(1.12) translate(-2%, -1%); }
}
.nh-hero-bg--no-anim .nh-hero-bg-img { animation: none !important; }

/* Bottom gradient — transparent to bg */
.nh-hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    transparent 25%,
    rgba(5,5,15,.3) 45%,
    rgba(5,5,15,.7) 70%,
    var(--bg, #05050f) 100%
  );
  z-index: 1;
}

/* Side gradient for text readability */
.nh-hero-gradient-side {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(5,5,15,.65) 0%, rgba(5,5,15,.2) 40%, transparent 60%);
  z-index: 1;
}

/* Content — positioned bottom-left */
.nh-hero-content {
  position: absolute;
  bottom: 40px;
  left: 40px;
  max-width: 600px;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nh-hero-badge {
  font-family: 'Orbitron', sans-serif;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--pl, #00d4ff);
  padding: 4px 12px;
  border-radius: 6px;
  background: rgba(0,212,255,.1);
  border: 1px solid rgba(0,212,255,.2);
  width: fit-content;
  backdrop-filter: blur(8px);
}

.nh-hero-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 36px;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 0 40px var(--pglow, rgba(0,212,255,.4)), 0 2px 12px rgba(0,0,0,.8);
  line-height: 1.1;
  letter-spacing: .02em;
}

.nh-hero-genres {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.nh-hero-genre {
  padding: 3px 12px;
  border-radius: 6px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.1);
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,.6);
}

.nh-hero-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.nh-hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 24px;
  border-radius: 8px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all .2s;
}

.nh-hero-btn--primary {
  background: linear-gradient(135deg, var(--pl, #00d4ff), var(--pl2, #7b2fff));
  color: #fff;
  box-shadow: 0 4px 20px var(--pglow2, rgba(0,212,255,.25));
}

.nh-hero-btn--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px var(--pglow, rgba(0,212,255,.4));
}

/* Dot indicators */
.nh-hero-dots {
  position: absolute;
  bottom: 40px;
  right: 40px;
  z-index: 2;
  display: flex;
  gap: 8px;
  align-items: center;
}

.nh-hero-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,.25);
  border: none;
  cursor: pointer;
  padding: 0;
  transition: all .2s;
}

.nh-hero-dot:hover {
  background: rgba(255,255,255,.5);
}

.nh-hero-dot.active {
  background: var(--pl, #00d4ff);
  box-shadow: 0 0 8px var(--pglow, rgba(0,212,255,.6));
  width: 24px;
  border-radius: 4px;
}


/* ═══════════════════════════════════════════════════════════════════════════
   RECENTLY ADDED ROWS
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-recent {
  display: flex;
  flex-direction: column;
  padding: 0 28px;
  margin-top: 36px;
  overflow: visible;
}

.nh-recent:last-child {
  padding-bottom: 48px;
}

/* ── Section headers ─────────────────────────────────────────────────────── */
.nh-section-head {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 18px;
}
.nh-section-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 10px; font-weight: 700;
  letter-spacing: .2em; text-transform: uppercase;
  color: var(--pl, #00d4ff);
}
.nh-section-link {
  display: inline-flex; align-items: center; gap: 5px;
  cursor: pointer; background: none; border: none; font-family: inherit; padding: 0;
  color: var(--pl); transition: all .2s;
}
.nh-section-link:hover { text-shadow: 0 0 12px var(--pglow); }

.nh-row-nav { display: flex; gap: 6px; }
.nh-nav-btn {
  width: 28px; height: 28px; border-radius: 8px;
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(255,255,255,.08);
  color: var(--text); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s;
}
.nh-nav-btn:hover {
  border-color: var(--pl);
  background: rgba(0,212,255,.08);
  box-shadow: 0 0 8px var(--pglow2);
}

/* ── Horizontal scroll ───────────────────────────────────────────────────── */
.nh-scroll {
  display: flex; gap: 14px;
  overflow-x: auto;
  padding-top: 12px; padding-bottom: 12px;
  scroll-behavior: smooth; scrollbar-width: none;
}
.nh-scroll::-webkit-scrollbar { display: none; }


/* ── Cover cards ─────────────────────────────────────────────────────────── */
.nh-cover-card {
  flex: 0 0 auto; width: 150px; cursor: pointer;
  transition: transform .3s cubic-bezier(.25,.46,.45,.94);
}
.nh-cover-card:hover {
  transform: translateY(-8px);
}

.nh-cover-img-wrap {
  width: 150px; aspect-ratio: 3/4;
  border-radius: 12px; overflow: hidden;
  position: relative;
  background: var(--bg2, #0a0a1a);
  border: 1px solid var(--glass-border, rgba(0,212,255,.12));
  box-shadow: 0 4px 20px rgba(0,0,0,.4), 0 0 8px var(--pglow2, rgba(0,212,255,.08));
  transition: all .3s cubic-bezier(.25,.46,.45,.94);
}

.nh-cover-card:hover .nh-cover-img-wrap {
  border-color: var(--pl);
  box-shadow:
    0 20px 50px rgba(0,0,0,.6),
    0 0 24px var(--pglow2, rgba(0,212,255,.25));
}

.nh-cover-img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform .3s;
}
.nh-cover-card:hover .nh-cover-img { transform: scale(1.06); }
.nh-cover-fallback { width: 100%; height: 100%; background: rgba(255,255,255,.03); }

.nh-cover-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,.9) 0%, transparent 50%);
  display: flex; align-items: flex-end; padding: 10px;
  opacity: 0; transition: opacity .2s;
}
.nh-cover-card:hover .nh-cover-overlay { opacity: 1; }

.nh-cover-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 9px; font-weight: 700; color: #fff;
  letter-spacing: .03em; line-height: 1.3;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  text-shadow: 0 0 8px var(--pglow);
}

.nh-cover-label {
  font-size: 11px; color: var(--muted); margin-top: 8px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  font-weight: 600;
}


/* ═══════════════════════════════════════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════════════════════════════════════ */
@media (max-width: 1100px) {
  .nh-hero { height: 360px; }
  .nh-hero-title { font-size: 28px; }
}

@media (max-width: 768px) {
  .nh-hero { height: 300px; }
  .nh-hero-content {
    bottom: 24px;
    left: 20px;
    right: 20px;
    max-width: none;
  }
  .nh-hero-title { font-size: 22px; }
  .nh-hero-badge { font-size: 8px; }
  .nh-hero-dots {
    bottom: 24px;
    right: 20px;
  }
  .nh-recent { padding: 0 12px; margin-top: 24px; }
  .nh-cover-card { width: 110px; }
  .nh-cover-img-wrap { width: 110px; }
}
</style>
