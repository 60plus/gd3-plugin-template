<template>
  <div class="cp" :style="{ '--sys-color': sysColor }">

    <!-- NH background: same as main theme (orbs, particles, grid, scanlines) -->
    <AmbientBackground />
    <div v-if="nhParticles > 0" class="cp-nh-particles">
      <div v-for="i in nhParticles" :key="i" class="cp-nh-particle" :style="{ left:(5+((i*13+7)%85))+'%', animationDuration:(8+(i*1.3)%6)+'s', animationDelay:(i*1.2)+'s', width:(1.5+(i%3))+'px', height:(1.5+(i%3))+'px' }" />
    </div>
    <div v-if="nhGrid" class="cp-nh-grid" />
    <div v-if="nhScanlines" class="cp-nh-scanlines" />

    <!-- ═══ SYSTEM VIEW — Colorful Pop 1:1 ═══════════════════════════ -->
    <template v-if="state === 'systems'">
      <div class="cp-bg" />

      <!-- Right color block with artwork background (pos 0.359, size 0.615 x 0.91) -->
      <div class="cp-sys-block" :style="{ backgroundColor: sysColor + '1a' }">
        <img v-if="currentPlatform" :src="videoHeroUrl || pluginAsset('artwork/' + currentPlatform.fs_slug + '.webp')" :key="videoHeroUrl || currentPlatform.fs_slug" class="cp-sys-block-art" :class="{ 'cp-sys-block-art--static': !kenBurnsEnabled }" @error="(e:any) => e.target.style.opacity='0'" />
      </div>

      <!-- Pop / Overlay+Video cycle -->
      <div class="cp-sys-img-wrap">
        <!-- Pop artwork (default, fades out when overlay active) -->
        <img
          v-if="currentPlatform"
          :src="pluginAsset('pop/' + currentPlatform.fs_slug + '.webp')"
          class="cp-sys-img cp-sys-img--pop"
          :class="{ 'cp-sys-img--hidden': showPhase === 'overlay' }"
        />
        <!-- Overlay: video UNDER transparent overlay image (TV cutout = alpha) -->
        <div
          v-if="currentPlatform"
          class="cp-sys-overlay-wrap"
          :class="{ 'cp-sys-overlay--visible': showPhase === 'overlay' }"
        >
          <!-- Video positioned exactly in TV cutout -->
          <video
            v-if="videoUrl && showPhase === 'overlay'"
            ref="videoRef"
            :src="videoUrl"
            class="cp-sys-video"
            :style="videoStyle"
            autoplay
            playsinline
            muted
            @ended="onVideoEnded"
            @error="onVideoEnded"
          />
          <div v-if="nhScanlines && videoUrl && showPhase === 'overlay'" class="cp-sys-video-scanlines" :style="videoStyle" />
          <!-- Overlay PNG with transparency ON TOP — acts as mask -->
          <img
            :src="pluginAsset('overlay/' + currentPlatform.fs_slug + '.webp')"
            class="cp-sys-overlay-img"
          />
          <!-- Wheel logo centered horizontally on video element -->
          <div v-if="showPhase === 'overlay' && videoUrl" class="cp-sys-video-wheel" :style="wheelStyle">
            <img v-if="videoWheelUrl" :src="videoWheelUrl" class="cp-sys-video-wheel-img" />
            <div v-else-if="videoRomName" class="cp-sys-video-wheel-text">{{ videoRomName }}</div>
          </div>
        </div>
      </div>

      <!-- Year (from metadata JSON) -->
      <div class="cp-sys-year" :style="{ color: sysColor }">{{ platMeta?.year || '' }}</div>

      <!-- Platform name as SVG logo (from plugin assets) -->
      <div class="cp-sys-name">
        <img :key="'logo-'+currentPlatform?.fs_slug" :src="pluginAsset('logos/' + (currentPlatform?.fs_slug||'') + '.svg')" class="cp-sys-name-logo" @error="onNameLogoError" />
        <span v-if="nameLogoFailed" class="cp-sys-name-text">{{ platMeta?.name || currentPlatform?.name || '' }}</span>
      </div>

      <!-- Description (from metadata JSON — with translations) -->
      <div class="cp-sys-desc">{{ platDescription }}</div>

      <!-- Bottom 3 color blocks: icon (dark) | game count (normal) | colored icon (light) -->
      <div class="cp-sys-bottom">
        <div class="cp-sys-bottom-block cp-sys-bottom-block--dark">
          <img :key="'wicon-'+currentPlatform?.fs_slug" :src="'/platforms/icons/' + (currentPlatform?.fs_slug||'') + '.png'" class="cp-sys-bottom-icon" />
          <div class="cp-sys-bottom-num">{{ currentPlatform?.rom_count || 0 }}</div>
          <div class="cp-sys-bottom-label">GAMES</div>
        </div>
        <div class="cp-sys-bottom-block">
          <img :src="pluginAsset('images/badge-favorite.svg')" class="cp-sys-bottom-fav-icon" />
          <div class="cp-sys-bottom-num">{{ platformFavCount }}</div>
          <div class="cp-sys-bottom-label">FAVORITES</div>
        </div>
        <div class="cp-sys-bottom-block cp-sys-bottom-block--light">
          <!-- Colored icon from plugin assets -->
          <img :src="pluginAsset('icons/' + (currentPlatform?.fs_slug||'') + '.png')" class="cp-sys-bottom-icon-color" :class="iconAnimEnabled ? 'cp-icon-anim--' + iconAnimStyle : ''" />
        </div>
      </div>



      <div class="cp-help">
        <span class="cp-help-item"><svg class="cp-help-icon" viewBox="0 0 24 24"><path d="M7 10l5-5 5 5H7zm0 4l5 5 5-5H7z" fill="currentColor"/></svg> Navigate</span>
        <span class="cp-help-item"><svg class="cp-help-icon" viewBox="0 0 24 24"><path d="M10 7l-5 5 5 5V7zm4 0v10l5-5-5-5z" fill="currentColor"/></svg> ★ Favorites / ⏱ Recent</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="currentColor">A</text></svg> Select</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="currentColor">B</text></svg> Back</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn-wide" viewBox="0 0 36 24"><rect x="1" y="4" width="34" height="16" rx="8" fill="currentColor" opacity=".3"/><rect x="1" y="4" width="34" height="16" rx="8" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="18" y="16" text-anchor="middle" font-size="8" font-weight="bold" fill="currentColor">START</text></svg> Menu</span>
      </div>
    </template>

    <!-- ═══ GAME LIST — list-video (Pop style: text list + big image) ══ -->
    <template v-if="state === 'games-list' || ((state === 'favorites' || state === 'recent') && gameView === 'list')">
      <div class="cp-bg" />
      <!-- Colored panel behind list -->
      <div class="cp-gl-panel" />

      <!-- System logo (top, above list) -->
      <div class="cp-gl-syslogo-wrap">
        <template v-if="state === 'favorites'">
          <span class="cp-sys-special-title">★ Favorites</span>
        </template>
        <template v-else-if="state === 'recent'">
          <span class="cp-sys-special-title">⏱ Recently Played</span>
        </template>
        <template v-else>
          <img :src="'/platforms/icons/' + (currentPlatform?.fs_slug||'') + '.png'" class="cp-gl-syslogo-icon" @error="(e:any) => e.target.style.display='none'" />
          <img :src="'/platforms/names/' + (currentPlatform?.fs_slug||'') + '.svg'" class="cp-gl-syslogo-name" @error="(e:any) => e.target.style.display='none'" />
        </template>
      </div>

      <!-- Text list (just names, no covers — like Pop) -->
      <div class="cp-gl-list" ref="gameListRef">
        <div
          v-for="(rom, i) in roms" :key="rom.id"
          class="cp-gl-row"
          :class="{ selected: i === romIdx }"
          @click="romIdx = i"
        ><span v-if="isFavorite(rom.id)" class="cp-gl-fav-star">★</span>{{ rom.title }}</div>
      </div>

      <!-- Hero background with cover inside (right of panel) -->
      <div class="cp-gl-hero" v-if="selectedRom">
        <img :src="selectedRom.background_path || selectedRom.cover_path || ''" class="cp-gl-hero-img" :class="{ 'cp-gl-hero-img--static': !kenBurnsEnabled }" />
        <div class="cp-gl-hero-fade" />
        <div class="cp-gl-bigimage">
          <img v-if="selectedRom?.cover_path" :src="selectedRom.cover_path" class="cp-gl-bigimage-img" />
        </div>
      </div>

      <!-- Overlay + video (right-top — console with game video in TV) -->
      <div class="cp-gl-overlay-wrap" v-if="currentPlatform">
        <video
          v-if="selectedRom?.video_path"
          :key="selectedRom.id"
          ref="glVideoRef"
          :src="selectedRom.video_path"
          class="cp-gl-overlay-video"
          :style="videoStyle"
          autoplay muted playsinline loop
          @canplay="onGlVideoCanPlay"
        />
        <div v-if="nhScanlines && selectedRom?.video_path" class="cp-sys-video-scanlines" :style="videoStyle" />
        <img :src="pluginAsset('overlay/' + currentPlatform.fs_slug + '.webp')" class="cp-gl-overlay-img" />
      </div>

      <!-- Info panel (bottom right, under cover+overlay) -->
      <div class="cp-gl-info">
        <div v-if="detail?.wheel_path" class="cp-gl-info-wheel"><img :src="detail.wheel_path" class="cp-gl-info-wheel-img" /></div>
        <div v-else class="cp-gl-info-title">{{ selectedRom?.title || '' }}</div>
        <div class="cp-gl-info-meta">
          <span v-if="detail?.ss_score" class="cp-gl-info-rating" :style="{color:sysColor}">{{ '★'.repeat(Math.round(detail.ss_score/4)) }}{{ '☆'.repeat(5-Math.round(detail.ss_score/4)) }} {{ (detail.ss_score/2).toFixed(1) }}</span>
          <span v-if="detail?.release_year || selectedRom?.release_year">{{ detail?.release_year || selectedRom?.release_year }}</span>
          <span v-if="detail?.player_count">{{ detail.player_count }} Player{{ detail.player_count > 1 ? 's' : '' }}</span>
        </div>
        <div v-if="detail?.genres?.length" class="cp-gl-info-genres">
          <span v-for="g in detail.genres.slice(0,3)" :key="g" class="cp-gl-info-genre" :style="{borderColor:sysColor,color:sysColor}">{{ g }}</span>
        </div>
        <div v-if="detail?.developer || detail?.publisher" class="cp-gl-info-devpub">
          <span v-if="detail?.developer" class="cp-gl-info-company">
            <img v-if="detail.developer_ss_id" :src="`https://screenscraper.fr/image.php?companyid=${detail.developer_ss_id}&media=logo-monochrome&maxwidth=110`" class="cp-gl-info-company-logo" @error="(e:any) => { e.target.style.display='none'; e.target.nextElementSibling && (e.target.nextElementSibling.style.display='inline') }" />
            <span :style="detail.developer_ss_id ? {display:'none'} : {}">{{ detail.developer }}</span>
          </span>
          <span v-if="detail?.developer && detail?.publisher" class="cp-gl-info-sep"> · </span>
          <span v-if="detail?.publisher" class="cp-gl-info-company">
            <img v-if="detail.publisher_ss_id" :src="`https://screenscraper.fr/image.php?companyid=${detail.publisher_ss_id}&media=logo-monochrome&maxwidth=110`" class="cp-gl-info-company-logo" @error="(e:any) => { e.target.style.display='none'; e.target.nextElementSibling && (e.target.nextElementSibling.style.display='inline') }" />
            <span :style="detail.publisher_ss_id ? {display:'none'} : {}">{{ detail.publisher }}</span>
          </span>
        </div>
        <div v-if="detail?.description" class="cp-gl-info-desc">{{ detail.description }}</div>
        <div v-if="detail?.hltb_main_s || detail?.hltb_complete_s" class="cp-gl-info-hltb">
          <span v-if="detail?.hltb_main_s">🕐 Main: {{ fmtHltb(detail.hltb_main_s) }}</span>
          <span v-if="detail?.hltb_extra_s">Extras: {{ fmtHltb(detail.hltb_extra_s) }}</span>
          <span v-if="detail?.hltb_complete_s">100%: {{ fmtHltb(detail.hltb_complete_s) }}</span>
        </div>
      </div>

      <div class="cp-help">
        <span class="cp-help-item"><svg class="cp-help-icon" viewBox="0 0 24 24"><path d="M7 10l5-5 5 5H7zm0 4l5 5 5-5H7z" fill="currentColor"/></svg> Games</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="currentColor">A</text></svg> Play</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="currentColor">B</text></svg> Back</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="currentColor">X</text></svg> Screenshots</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="currentColor">Y</text></svg> ★ Favorite</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn-wide" viewBox="0 0 36 24"><rect x="1" y="4" width="34" height="16" rx="8" fill="currentColor" opacity=".3"/><rect x="1" y="4" width="34" height="16" rx="8" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="18" y="16" text-anchor="middle" font-size="8" font-weight="bold" fill="currentColor">START</text></svg> Menu</span>
      </div>
    </template>


    <!-- ═══ GAME CAROUSEL — full-screen fanart (Pop style) ═════════════ -->
    <template v-if="state === 'games-carousel' || ((state === 'favorites' || state === 'recent') && gameView === 'carousel')">
      <!-- Full-screen game artwork -->
      <div class="cp-gc-bg">
        <transition name="cp-slide" mode="out-in">
          <img v-if="selectedRom" :key="selectedRom.id" :src="selectedRom.background_path || selectedRom.cover_path || ''" class="cp-gc-bg-img" />
        </transition>
      </div>
      <div class="cp-gc-dim" />

      <!-- System name (top left) -->
      <div class="cp-gc-sysname">{{ state === 'favorites' ? '★ Favorites' : state === 'recent' ? '⏱ Recently Played' : currentPlatform?.name || '' }}</div>

      <!-- Game name (bottom left, big) -->
      <div class="cp-gc-gamename">{{ selectedRom?.title || '' }}</div>

      <!-- Year (bottom left, small) -->
      <div class="cp-gc-year">{{ selectedRom?.release_year || '' }}</div>

      <div class="cp-help">
        <span class="cp-help-item"><svg class="cp-help-icon" viewBox="0 0 24 24"><path d="M10 7l-5 5 5 5V7zm4 0v10l5-5-5-5z" fill="currentColor"/></svg> Games</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="currentColor">A</text></svg> Play</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".3"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="currentColor">B</text></svg> Back</span>
        <span class="cp-help-item"><svg class="cp-help-icon cp-help-btn-wide" viewBox="0 0 36 24"><rect x="1" y="4" width="34" height="16" rx="8" fill="currentColor" opacity=".3"/><rect x="1" y="4" width="34" height="16" rx="8" stroke="currentColor" stroke-width="1.5" fill="none"/><text x="18" y="16" text-anchor="middle" font-size="8" font-weight="bold" fill="currentColor">START</text></svg> Menu</span>
      </div>
    </template>

    <!-- ═══ OVERLAYS ═══════════════════════════════════════════════════ -->
    <transition name="cp-fade">
      <div v-if="menuOpen" class="cp-overlay" @click.self="menuOpen=false">
        <div class="cp-menu">
          <div class="cp-menu-title" :style="{color:sysColor}">SETTINGS</div>
          <!-- Tabs -->
          <div class="cp-menu-tabs">
            <button class="cp-menu-tab" :class="{active:menuTab==='general'}" @click="menuTab='general';menuIdx=0">General</button>
            <button class="cp-menu-tab" :class="{active:menuTab==='visuals'}" @click="menuTab='visuals';menuIdx=0">Visuals</button>
          </div>
          <!-- General tab -->
          <template v-if="menuTab==='general'">
            <div v-for="(m,i) in menuItemsGeneral" :key="'g'+i" class="cp-menu-row" :class="{focus:menuIdx===i,danger:m.danger}" @click="m.action">{{m.label}}</div>
          </template>
          <!-- Visuals tab -->
          <template v-if="menuTab==='visuals'">
            <div v-for="(m,i) in menuItemsVisuals" :key="'v'+i" class="cp-menu-row" :class="{focus:menuIdx===i}" @click="m.action">{{m.label}}</div>
          </template>
          <div class="cp-menu-hint">↑↓ Navigate · ←→ Tabs · A Toggle · B Close</div>
        </div>
      </div>
    </transition>
    <transition name="cp-fade">
      <div v-if="exitOpen" class="cp-overlay" @click.self="exitOpen=false">
        <div class="cp-menu" style="width:280px;text-align:center">
          <div class="cp-menu-title">Exit Couch Mode?</div>
          <div class="cp-menu-row" :class="{focus:exitIdx===0}" @click="exitOpen=false">Stay</div>
          <div class="cp-menu-row danger" :class="{focus:exitIdx===1}" @click="doExit">Exit</div>
        </div>
      </div>
    </transition>
    <transition name="cp-fade">
      <div v-if="shotIdx>=0 && detail?.screenshots" class="cp-overlay" @click.self="shotIdx=-1">
        <img :src="detail.screenshots[shotIdx]" class="cp-shot-img" />
        <div class="cp-shot-ctr">{{shotIdx+1}} / {{detail.screenshots.length}}</div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const _gd = (window as any).__GD__
const client = _gd.api
const router = useRouter()
const { useCouchNav, couchNavPaused } = _gd.composables
const getEjsCore = _gd.getEjsCore

interface Platform { id:number; slug:string; fs_slug:string; name:string; rom_count:number; description:string|null; manufacturer:string|null; release_year_platform:number|null; generation:number|null; wheel_path:string|null }
interface Rom { id:number; slug:string; title:string; cover_path:string|null; background_path:string|null; wheel_path:string|null; video_path:string|null; release_year:number|null; bezel_path:string|null }
interface Detail { description:string|null; screenshots:string[]|null; developer:string|null; developer_ss_id:number|null; publisher:string|null; publisher_ss_id:number|null; genres:string[]|null; ss_score:number|null; wheel_path:string|null; hltb_main_s:number|null; hltb_extra_s:number|null; hltb_complete_s:number|null; player_count:number|null; release_year:number|null }

// Plugin asset URL helper
const PLUGIN_ID = 'neon-horizon'
function pluginAsset(path: string): string {
  return `/api/plugins/${PLUGIN_ID}/assets/${path}`
}

// Platform metadata (loaded from plugin's platforms.json)
const platformsJson = ref<Record<string, any>>({})
async function loadPlatformsJson() {
  try {
    const { data } = await client.get(`/plugins/${PLUGIN_ID}/assets/platforms.json`)
    platformsJson.value = typeof data === 'object' ? data : {}
  } catch (e) { console.warn('[CP] Could not load platforms.json:', e) }
}

const platMeta = computed(() => {
  const slug = currentPlatform.value?.fs_slug
  return slug ? platformsJson.value[slug] ?? null : null
})

// System color from metadata (Colorful Pop's systemColor) — fallback to hardcoded
const sysColorFromMeta = computed(() => {
  const c = platMeta.value?.color
  return c ? '#' + c : null
})

// Description with browser language support
const platDescription = computed(() => {
  const meta = platMeta.value
  if (!meta) return currentPlatform.value?.description || ''
  // Try browser language
  const lang = navigator.language?.replace('-', '_') || 'en'
  const translations = meta.translations || {}
  // Try exact match (e.g. pl_PL), then prefix (pl), then English default
  if (translations[lang]) return translations[lang]
  const prefix = lang.split('_')[0]
  for (const key of Object.keys(translations)) {
    if (key.startsWith(prefix)) return translations[key]
  }
  return meta.description || currentPlatform.value?.description || ''
})

type State = 'systems'|'games-list'|'games-carousel'|'favorites'|'recent'
const state = ref<State>('systems')
const platforms = ref<Platform[]>([])
const sysIdx = ref(0)
const roms = ref<Rom[]>([])
const romIdx = ref(0)
const detail = ref<Detail|null>(null)
const cache = new Map<number,Detail>()

// ── Favorites & Recently Played ──────────────────────────────────
interface SavedRom { id:number; title:string; cover_path:string|null; cover_aspect:string|null; platform_slug:string; platform_fs_slug:string; platform_name:string }

const favorites = ref<SavedRom[]>(JSON.parse(localStorage.getItem('nh_couch_favorites')||'[]'))
const recentlyPlayed = ref<SavedRom[]>(JSON.parse(localStorage.getItem('nh_couch_recent')||'[]'))

function saveFavorites() { localStorage.setItem('nh_couch_favorites', JSON.stringify(favorites.value)) }
function saveRecent() { localStorage.setItem('nh_couch_recent', JSON.stringify(recentlyPlayed.value)) }

function isFavorite(romId: number): boolean { return favorites.value.some(f => f.id === romId) }
function fmtHltb(s: number): string { const h = Math.floor(s/3600); const m = Math.round((s%3600)/60); return h > 0 ? `${h}h ${m}m` : `${m}m` }

// Auto-scroll description if overflowing
let _descScrollTimer: ReturnType<typeof setInterval>|null = null
function startDescAutoScroll() {
  stopDescAutoScroll()
  _descScrollTimer = setTimeout(() => {
    const el = document.querySelector('.cp-gl-info-desc') as HTMLElement
    if (!el || el.scrollHeight <= el.clientHeight) return
    let dir = 1
    _descScrollTimer = setInterval(() => {
      el.scrollTop += dir
      if (el.scrollTop >= el.scrollHeight - el.clientHeight) dir = -1
      if (el.scrollTop <= 0) dir = 1
    }, 50) as any
  }, 2000)
}
function stopDescAutoScroll() {
  if (_descScrollTimer) { clearTimeout(_descScrollTimer); clearInterval(_descScrollTimer); _descScrollTimer = null }
}

const platformFavCount = computed(() => {
  const fs = currentPlatform.value?.fs_slug
  if (!fs) return 0
  return favorites.value.filter(f => f.platform_fs_slug === fs).length
})

function toggleFavorite() {
  const rom = selectedRom.value
  if (!rom) return
  const idx = favorites.value.findIndex(f => f.id === rom.id)
  if (idx >= 0) {
    favorites.value.splice(idx, 1)
  } else {
    // Get platform info from currentPlatform or from saved favorites/recent
    const plat = currentPlatform.value
    const saved = [...favorites.value, ...recentlyPlayed.value].find(f => f.id === rom.id)
    favorites.value.unshift({
      id: rom.id, title: rom.title, cover_path: rom.cover_path,
      cover_aspect: rom.cover_aspect,
      platform_slug: plat?.slug || saved?.platform_slug || '',
      platform_fs_slug: plat?.fs_slug || saved?.platform_fs_slug || '',
      platform_name: plat?.name || saved?.platform_name || '',
    })
  }
  saveFavorites()
}

function addToRecent(rom: Rom, plat: Platform) {
  const existing = recentlyPlayed.value.findIndex(r => r.id === rom.id)
  if (existing >= 0) recentlyPlayed.value.splice(existing, 1)
  recentlyPlayed.value.unshift({
    id: rom.id, title: rom.title, cover_path: rom.cover_path,
    cover_aspect: rom.cover_aspect, platform_slug: plat.slug,
    platform_fs_slug: plat.fs_slug, platform_name: plat.name,
  })
  if (recentlyPlayed.value.length > 50) recentlyPlayed.value.length = 50
  saveRecent()
}

// Current list for favorites/recent views (reuse roms array)
function enterFavorites() {
  stopCycle()
  roms.value = favorites.value.map(f => ({ id:f.id, slug:'', title:f.title, cover_path:f.cover_path, cover_aspect:f.cover_aspect, background_path:null, wheel_path:null, video_path:null, release_year:null, bezel_path:null }))
  romIdx.value = 0; detail.value = null
  state.value = 'favorites'
}
function enterRecent() {
  stopCycle()
  roms.value = recentlyPlayed.value.map(f => ({ id:f.id, slug:'', title:f.title, cover_path:f.cover_path, cover_aspect:f.cover_aspect, background_path:null, wheel_path:null, video_path:null, release_year:null, bezel_path:null }))
  romIdx.value = 0; detail.value = null
  state.value = 'recent'
}

// Select button polling — same pattern as useCouchNav (requestAnimationFrame)
let _selFrame = 0
let _selLastPress = 0
const SEL_COOLDOWN = 300

function pollSelectButton() {
  _selFrame = requestAnimationFrame(pollSelectButton)
  if (!document.hasFocus()) return
  const gps = navigator.getGamepads?.() ?? []
  for (const gp of gps) {
    if (!gp) continue
    // Y = button 3 (Xbox), Triangle = button 3 (PS)
    if (gp.buttons[3]?.pressed) {
      const now = Date.now()
      if (now - _selLastPress < SEL_COOLDOWN) return
      _selLastPress = now
      if ((state.value === 'games-list' || state.value === 'games-carousel' || state.value === 'favorites' || state.value === 'recent') && selectedRom.value) {
        toggleFavorite()
      }
      return
    }
  }
}

// Keyboard: F key = toggle favorite (same as Y button on gamepad)
function onKeyFavorite(e: KeyboardEvent) {
  if (e.key === 'f' || e.key === 'F') {
    e.preventDefault()
    if ((state.value === 'games-list' || state.value === 'games-carousel' || state.value === 'favorites' || state.value === 'recent') && selectedRom.value) {
      toggleFavorite()
    }
  }
}
const gameView = ref<'list'|'carousel'>(localStorage.getItem('gd3_couch_view') as any||'list')
const menuOpen = ref(false); const menuIdx = ref(0)
const exitOpen = ref(false); const exitIdx = ref(0)
const shotIdx = ref(-1)
const gameListRef = ref<HTMLElement|null>(null)
const loaded = new Set<string>()
const launchMode = ref(localStorage.getItem('gd3_couch_launch')||'tab')
const bezelOn = ref(localStorage.getItem('gd3_couch_bezel')==='on')
const nameLogoFailed = ref(false)
function onNameLogoError(e: Event) { (e.target as HTMLImageElement).style.display = 'none'; nameLogoFailed.value = true }

// NH theme background settings (polled from CSS vars, same as NeonHorizonLayout)
const nhParticles = ref(6)
const nhGrid = ref(false)
const nhScanlines = ref(false)

function pollNhSettings() {
  const cs = getComputedStyle(document.documentElement)
  const pc = cs.getPropertyValue('--nh-particle-count').trim()
  nhParticles.value = pc !== '' ? Number(pc) : 6
  nhScanlines.value = cs.getPropertyValue('--nh-scanlines').trim() === '1'
  nhGrid.value = document.documentElement.getAttribute('data-grid') === 'true'
}

// Menu tabs
const menuTab = ref<'general'|'visuals'>('general')

// ── Pop / Overlay + Video cycle ──────────────────────────────────────
const showPhase = ref<'pop'|'overlay'>('pop')
const videoUrl = ref<string|null>(null)
const videoHeroUrl = ref<string|null>(null)
const videoWheelUrl = ref<string|null>(null)  // wheel logo of ROM being played
const videoRomName = ref<string|null>(null)   // fallback name if no wheel
const videoRef = ref<HTMLVideoElement|null>(null)
const glVideoRef = ref<HTMLVideoElement|null>(null)

function onGlVideoCanPlay() {
  const el = glVideoRef.value
  if (el && videoVolume.value > 0) {
    el.volume = videoVolume.value / 100
    try { el.muted = false } catch {}
  }
}
const videoPosData = ref<Record<string, {x:number,y:number,w:number,h:number}>>({})
const platformVideos = new Map<string, string[]>()

const videoStyle = computed(() => {
  const slug = currentPlatform.value?.fs_slug || ''
  const vp = videoPosData.value[slug]
  if (!vp) return { left: '45%', top: '30%', width: '30%', height: '25%' }
  return { left: vp.x + '%', top: vp.y + '%', width: vp.w + '%', height: vp.h + '%' }
})

// Game list video: same positions work because overlay img uses object-fit:contain
// Both system view and game list overlays render the image at same aspect ratio
const glVideoStyle = computed(() => videoStyle.value)

// Wheel logo: same left + width as video, centered inside
const wheelStyle = computed(() => {
  const slug = currentPlatform.value?.fs_slug || ''
  const vp = videoPosData.value[slug]
  if (!vp) return { left: '40%', width: '20%' }
  return { left: vp.x + '%', width: vp.w + '%' }
})

async function loadVideoPos() {
  try {
    const { data } = await client.get(`/plugins/${PLUGIN_ID}/assets/videopos.json?_=${Date.now()}`)
    videoPosData.value = typeof data === 'object' ? data : {}
  } catch {}
}
const videoCycleEnabled = ref(localStorage.getItem('nh_couch_videocycle') !== 'off')
const videoVolume = ref(Number(localStorage.getItem('nh_couch_video_vol') ?? 50))

function cycleVolume() {
  const levels = [0, 25, 50, 75, 100]
  const i = (levels.indexOf(videoVolume.value) + 1) % levels.length
  videoVolume.value = levels[i] ?? 50
  localStorage.setItem('nh_couch_video_vol', String(videoVolume.value))
  applyVolume()
}
function applyVolume() {
  const el = videoRef.value
  if (!el) return
  el.volume = videoVolume.value / 100
  // Unmute after autoplay started (user already interacted with page via gamepad/keyboard)
  if (videoVolume.value > 0) {
    try { el.muted = false } catch { /* autoplay policy */ }
  } else {
    el.muted = true
  }
}
let cycleTimer: ReturnType<typeof setTimeout>|null = null


interface VideoRom { video_path: string; background_path: string | null; cover_path: string | null; wheel_path: string | null; name: string }
const platformVideoRoms = new Map<string, VideoRom[]>()

async function fetchPlatformVideoRoms(slug: string): Promise<VideoRom[]> {
  if (platformVideoRoms.has(slug)) return platformVideoRoms.get(slug)!
  try {
    const { data } = await client.get('/roms', { params: { platform_slug: slug, limit: 500, offset: 0 } })
    const items = data.items ?? (Array.isArray(data) ? data : [])
    const vr = items.filter((r: any) => r.video_path).map((r: any) => ({
      video_path: r.video_path as string,
      background_path: r.background_path as string | null,
      cover_path: r.cover_path as string | null,
      wheel_path: r.wheel_path as string | null,
      name: (r.name || r.fs_name_no_ext || '') as string,
    }))
    platformVideoRoms.set(slug, vr)
    return vr
  } catch { return [] }
}

function stopCycle() {
  if (cycleTimer) { clearTimeout(cycleTimer); cycleTimer = null }
  showPhase.value = 'pop'
  videoUrl.value = null
  videoHeroUrl.value = null
  videoWheelUrl.value = null
  videoRomName.value = null
}

function startCycle() {
  stopCycle()
  if (!videoCycleEnabled.value || !currentPlatform.value || state.value !== 'systems') return
  // Wait 8s then show overlay + video
  cycleTimer = setTimeout(async () => {
    if (state.value !== 'systems') return  // user left systems view
    const apiSlug = currentPlatform.value?.slug
    if (!apiSlug) return
    const vRoms = await fetchPlatformVideoRoms(apiSlug)
    if (vRoms.length === 0) { startCycle(); return }
    // Pick random (different from last if possible)
    const pool = vRoms.length > 1 ? vRoms.filter(v => v.video_path !== videoUrl.value) : vRoms
    const picked = pool[Math.floor(Math.random() * pool.length)]
    videoUrl.value = picked.video_path
    videoHeroUrl.value = picked.background_path || picked.cover_path
    videoWheelUrl.value = picked.wheel_path
    videoRomName.value = picked.name
    showPhase.value = 'overlay'
    // Timeout: if video doesn't end in 20s, go back to pop
    cycleTimer = setTimeout(() => { onVideoEnded() }, 20000)
  }, 8000)
}

function onVideoEnded() {
  showPhase.value = 'pop'
  videoUrl.value = null
  videoHeroUrl.value = null
  videoWheelUrl.value = null
  videoRomName.value = null
  if (cycleTimer) clearTimeout(cycleTimer)
  startCycle()
}

function toggleVideoCycle() {
  videoCycleEnabled.value = !videoCycleEnabled.value
  localStorage.setItem('nh_couch_videocycle', videoCycleEnabled.value ? 'on' : 'off')
  if (videoCycleEnabled.value) startCycle(); else stopCycle()
}

// NH Couch visual settings (persisted to localStorage)
const kenBurnsEnabled = ref(localStorage.getItem('nh_couch_kenburns') !== 'off')
const iconAnimEnabled = ref(localStorage.getItem('nh_couch_iconanim') !== 'off')
const iconAnimStyle = ref(localStorage.getItem('nh_couch_iconanim_style') || 'shake')

function toggleKenBurns() {
  kenBurnsEnabled.value = !kenBurnsEnabled.value
  localStorage.setItem('nh_couch_kenburns', kenBurnsEnabled.value ? 'on' : 'off')
}
function toggleIconAnim() {
  iconAnimEnabled.value = !iconAnimEnabled.value
  localStorage.setItem('nh_couch_iconanim', iconAnimEnabled.value ? 'on' : 'off')
}
function cycleIconAnimStyle() {
  const styles = ['shake', 'spin', 'pop', 'bounce']
  const i = (styles.indexOf(iconAnimStyle.value) + 1) % styles.length
  iconAnimStyle.value = styles[i]
  localStorage.setItem('nh_couch_iconanim_style', iconAnimStyle.value)
}

const currentPlatform = computed(()=>platforms.value[sysIdx.value]??null)
const selectedRom = computed(()=>roms.value[romIdx.value]??null)
const sysColor = computed(()=>sysColorFromMeta.value||'#4466aa')

const menuItemsGeneral = computed(()=>[
  {label:`View: ${gameView.value}`,action:()=>{gameView.value=gameView.value==='list'?'carousel':'list';localStorage.setItem('gd3_couch_view',gameView.value)}},
  {label:`Launch: ${launchMode.value}`,action:()=>{const m=['tab','window','fullscreen'];launchMode.value=m[(m.indexOf(launchMode.value)+1)%3];localStorage.setItem('gd3_couch_launch',launchMode.value)}},
  {label:`Bezel: ${bezelOn.value?'ON':'OFF'}`,action:()=>{bezelOn.value=!bezelOn.value;localStorage.setItem('gd3_couch_bezel',bezelOn.value?'on':'off')}},
  {label:'Resume',action:()=>{menuOpen.value=false}},
  {label:'Exit',action:()=>doExit(),danger:true},
])
const menuItemsVisuals = computed(()=>[
  {label:`Ken Burns Animation: ${kenBurnsEnabled.value?'ON':'OFF'}`,action:toggleKenBurns},
  {label:`Video Cycle: ${videoCycleEnabled.value?'ON':'OFF'}`,action:toggleVideoCycle},
  {label:`Video Volume: ${videoVolume.value}%`,action:cycleVolume},
  {label:`Icon Animation: ${iconAnimEnabled.value?'ON':'OFF'}`,action:toggleIconAnim},
  {label:`Icon Style: ${iconAnimStyle.value}`,action:cycleIconAnimStyle},
])
const activeMenuItems = computed(()=>menuTab.value==='general'?menuItemsGeneral.value:menuItemsVisuals.value)

async function fetchPlatforms(){
  try{
    const{data}=await client.get('/roms/platforms')
    platforms.value=(Array.isArray(data)?data:[]).filter((p:any)=>p.rom_count>0).sort((a:any,b:any)=>a.name.localeCompare(b.name)).map((p:any)=>({
      id:p.id,slug:p.slug,fs_slug:p.fs_slug,name:p.custom_name||p.name,rom_count:p.rom_count,
      description:null,manufacturer:null,release_year_platform:null,generation:null,wheel_path:null,
    }))
    if(platforms.value.length)loadDetail(0)
  }catch(e){console.error('[CP]',e)}
}
async function loadDetail(idx:number){
  for(let d=-1;d<=1;d++){
    const i=idx+d;if(i<0||i>=platforms.value.length)continue
    const p=platforms.value[i];if(loaded.has(p.slug))continue;loaded.add(p.slug)
    try{const{data}=await client.get(`/roms/platforms/${p.slug}`);p.description=data.description??null;p.manufacturer=data.manufacturer??null;p.release_year_platform=data.release_year_platform??null;p.generation=data.generation??null}catch{}
  }
}
async function fetchRoms(){
  if(!currentPlatform.value)return
  try{const{data}=await client.get('/roms',{params:{platform_slug:currentPlatform.value.slug,limit:500,offset:0}});roms.value=(data.items??(Array.isArray(data)?data:[])).map((r:any)=>({id:r.id,slug:r.slug,title:r.name||r.fs_name_no_ext,cover_path:r.cover_path,background_path:r.background_path,wheel_path:r.wheel_path,video_path:r.video_path,release_year:r.release_year,bezel_path:r.bezel_path}));romIdx.value=0;detail.value=null}catch(e){console.error('[CP]',e)}
}
let dt:ReturnType<typeof setTimeout>|null=null
async function loadRom(rom:Rom){
  if(cache.has(rom.id)){detail.value=cache.get(rom.id)!;return}
  try{const{data}=await client.get(`/roms/${rom.id}`);const d:Detail={description:data.summary??null,screenshots:data.screenshots??null,developer:data.developer??null,developer_ss_id:data.developer_ss_id??null,publisher:data.publisher??null,publisher_ss_id:data.publisher_ss_id??null,genres:data.genres??null,ss_score:data.ss_score??null,wheel_path:data.wheel_path??null,hltb_main_s:data.hltb_main_s??null,hltb_extra_s:data.hltb_extra_s??null,hltb_complete_s:data.hltb_complete_s??null,player_count:data.player_count??null,release_year:data.release_year??null};cache.set(rom.id,d);if(selectedRom.value?.id===rom.id)detail.value=d}catch{}
}

function goSys(dir:number){const n=sysIdx.value+dir;if(n>=0&&n<platforms.value.length){sysIdx.value=n;loadDetail(n)}}
function selectPlatform(){stopCycle();state.value=gameView.value==='list'?'games-list':'games-carousel';fetchRoms()}
function backToSystems(){state.value='systems';roms.value=[];detail.value=null;startCycle()}
function doExit(){router.push('/')}
function launchGame(){
  const rom=selectedRom.value;if(!rom)return
  // Resolve platform — from currentPlatform or from favorites/recent saved data
  let fsSlug = currentPlatform.value?.fs_slug || ''
  let platSlug = currentPlatform.value?.slug || ''
  if ((state.value === 'favorites' || state.value === 'recent') && rom.id) {
    const saved = [...favorites.value, ...recentlyPlayed.value].find(f => f.id === rom.id)
    if (saved) { fsSlug = saved.platform_fs_slug; platSlug = saved.platform_slug }
  }
  const core=getEjsCore(fsSlug);if(!core)return
  // Add to recently played
  const plat = currentPlatform.value || { slug: platSlug, fs_slug: fsSlug, name: '' } as Platform
  addToRecent(rom, plat)
  const p:Record<string,string>={rom_id:String(rom.id),rom_name:rom.title,ejs_core:core,platform:fsSlug}
  if(bezelOn.value)p.bezel='1'
  const url='/player.html?'+new URLSearchParams(p).toString()
  if(launchMode.value==='fullscreen')window.location.href=url+'&returnTo=/couch'
  else if(launchMode.value==='window')window.open(url,'gd3-player','width=1280,height=720,menubar=no,toolbar=no')
  else window.open(url,'_blank')
  couchNavPaused.value=true;window.addEventListener('focus',()=>{couchNavPaused.value=false},{once:true})
}

watch(sysIdx,(i)=>{loadDetail(i);nameLogoFailed.value=false;startCycle()})
watch(videoUrl,(url)=>{ if(url) nextTick(()=>{ const el=videoRef.value; if(el){ el.play().then(()=>{ setTimeout(()=>applyVolume(),500) }).catch(()=>{}) } }) })
watch(romIdx,()=>{detail.value=null;shotIdx.value=-1;stopDescAutoScroll();if(dt)clearTimeout(dt);const r=selectedRom.value;if(r)dt=setTimeout(()=>loadRom(r),300);nextTick(()=>{(gameListRef.value?.querySelector('.cp-gl-row.selected') as HTMLElement)?.scrollIntoView({block:'nearest',behavior:'smooth'})})})
watch(detail,()=>{if(detail.value?.description)nextTick(()=>startDescAutoScroll())})
watch(gameView,(v)=>{if(state.value.startsWith('games-'))state.value=v==='list'?'games-list':'games-carousel'})

useCouchNav({
  up:()=>{if(menuOpen.value){menuIdx.value=Math.max(0,menuIdx.value-1);return}if(exitOpen.value){exitIdx.value=0;return}if(state.value==='systems')goSys(-1);if((state.value==='games-list'||state.value==='favorites'||state.value==='recent')&&romIdx.value>0)romIdx.value--},
  down:()=>{if(menuOpen.value){menuIdx.value=Math.min(activeMenuItems.value.length-1,menuIdx.value+1);return}if(exitOpen.value){exitIdx.value=1;return}if(state.value==='systems')goSys(1);if((state.value==='games-list'||state.value==='favorites'||state.value==='recent')&&romIdx.value<roms.value.length-1)romIdx.value++},
  left:()=>{if(menuOpen.value){menuTab.value=menuTab.value==='visuals'?'general':'visuals';menuIdx.value=0;return}if(shotIdx.value>0){shotIdx.value--;return}if(state.value==='systems'){enterFavorites();return}if((state.value==='games-carousel'||(state.value==='favorites'||state.value==='recent')&&gameView.value==='carousel')&&romIdx.value>0)romIdx.value--},
  right:()=>{if(menuOpen.value){menuTab.value=menuTab.value==='general'?'visuals':'general';menuIdx.value=0;return}if(shotIdx.value>=0&&detail.value?.screenshots&&shotIdx.value<detail.value.screenshots.length-1){shotIdx.value++;return}if(state.value==='systems'){enterRecent();return}if((state.value==='games-carousel'||(state.value==='favorites'||state.value==='recent')&&gameView.value==='carousel')&&romIdx.value<roms.value.length-1)romIdx.value++},
  confirm:()=>{if(menuOpen.value){activeMenuItems.value[menuIdx.value]?.action();return}if(exitOpen.value){exitIdx.value===1?doExit():(exitOpen.value=false);return}if(state.value==='systems')selectPlatform();else if(state.value==='favorites'||state.value==='recent')launchGame();else launchGame()},
  back:()=>{if(shotIdx.value>=0){shotIdx.value=-1;return}if(menuOpen.value){menuOpen.value=false;return}if(exitOpen.value){exitOpen.value=false;return}if(state.value==='favorites'||state.value==='recent'){backToSystems();return}if(state.value.startsWith('games-'))backToSystems();else exitOpen.value=true},
  menu:()=>{if(!exitOpen.value){menuOpen.value=!menuOpen.value;menuIdx.value=0}},
  x:()=>{if(detail.value?.screenshots?.length&&state.value.startsWith('games-'))shotIdx.value=0},
})

onMounted(()=>{document.documentElement.requestFullscreen?.().catch(()=>{});pollNhSettings();loadPlatformsJson();loadVideoPos();fetchPlatforms().then(()=>startCycle());_selFrame=requestAnimationFrame(pollSelectButton);document.addEventListener('keydown',onKeyFavorite)})
</script>

<style scoped>
.cp{position:fixed;inset:0;z-index:9999;overflow:hidden;user-select:none;font-family:'Rajdhani',sans-serif;color:#fff}
.cp-bg{position:absolute;inset:0;z-index:-1;background:var(--bg,#05050f)}

/* NH particles (same as NeonHorizonLayout) */
.cp-nh-particles{position:fixed;inset:0;z-index:1;pointer-events:none;overflow:hidden}
.cp-nh-particle{position:absolute;bottom:-10px;background:var(--pl,#00d4ff);border-radius:50%;opacity:0;animation:cp-nh-float 10s ease-in infinite;box-shadow:0 0 6px var(--pglow,rgba(0,212,255,.4))}
@keyframes cp-nh-float{0%{transform:translateY(0) scale(0);opacity:0}10%{opacity:.6}50%{opacity:.3}90%{opacity:.1}100%{transform:translateY(-110vh) scale(1.5);opacity:0}}

/* NH grid overlay */
.cp-nh-grid{position:fixed;inset:0;z-index:99;pointer-events:none;background-image:linear-gradient(rgba(0,212,255,.15) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,.15) 1px,transparent 1px);background-size:48px 48px;mix-blend-mode:screen}

/* NH scanlines */
.cp-nh-scanlines{position:fixed;inset:0;z-index:3;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.15) 2px,rgba(0,0,0,.15) 4px);mix-blend-mode:multiply}
.cp-fade-enter-active,.cp-fade-leave-active{transition:opacity .2s}.cp-fade-enter-from,.cp-fade-leave-to{opacity:0}
.cp-slide-enter-active,.cp-slide-leave-active{transition:opacity .35s}.cp-slide-enter-from,.cp-slide-leave-to{opacity:0}

/* ═══ SYSTEM VIEW ════════════════════════════════════════════════════ */
/* Right color block: pos 35.9% left, 4.5% top, 61.5% wide, 91% tall */
.cp-sys-block{position:absolute;left:35.9%;top:4.5%;width:61.5%;height:91%;z-index:2;overflow:hidden;background-color:color-mix(in srgb, var(--sys-color) 10%, transparent);-webkit-mask-image:linear-gradient(to right, transparent 0%, black 8%, black 92%, transparent 100%);mask-image:linear-gradient(to right, transparent 0%, black 8%, black 92%, transparent 100%)}
.cp-sys-block-art{position:absolute;inset:-5%;width:110%;height:110%;object-fit:cover;opacity:.35;animation:cp-kenburns 30s ease-in-out infinite alternate}
.cp-sys-block-art--static{animation:none!important;inset:0;width:100%;height:100%}
@keyframes cp-kenburns{0%{transform:scale(1) translate(0,0)}50%{transform:scale(1.08) translate(-2%,-1%)}100%{transform:scale(1.04) translate(1%,2%)}}
/* Platform image area — contains pop + overlay with crossfade */
.cp-sys-img-wrap{position:absolute;left:36.7%;top:4.5%;width:60%;height:91%;z-index:5;overflow:hidden}

/* Pop artwork */
.cp-sys-img--pop{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;transition:opacity .6s ease;z-index:2}
.cp-sys-img--hidden{opacity:0}

/* Overlay: video under transparent overlay image */
.cp-sys-overlay-wrap{position:absolute;inset:0;width:100%;height:100%;opacity:0;transition:opacity .6s ease;z-index:3}
.cp-sys-overlay--visible{opacity:1}
.cp-sys-overlay-img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;z-index:2;pointer-events:none}

/* Video positioned in TV cutout — coordinates from videopos.json (overlay-relative) */
.cp-sys-video{position:absolute;object-fit:cover;z-index:1}

/* Scanlines on video only (not on overlay/TV) */
.cp-sys-video-scanlines{position:absolute;z-index:1;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.15) 2px,rgba(0,0,0,.15) 4px)}

/* Wheel logo of playing ROM — bottom right of overlay */
.cp-sys-video-wheel{position:absolute;bottom:8%;z-index:3;display:flex;justify-content:center;opacity:0;animation:cp-wheel-in .6s ease .5s forwards}
.cp-sys-video-wheel-img{max-width:100%;max-height:8vh;object-fit:contain;filter:drop-shadow(0 2px 8px rgba(0,0,0,.7))}
.cp-sys-video-wheel-text{font-family:'Orbitron',sans-serif;font-size:clamp(14px,2.5vh,24px);font-weight:900;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.8)}
@keyframes cp-wheel-in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

/* Year: 2.6%, 15% */
.cp-sys-year{position:absolute;left:2.6%;top:15%;z-index:10;font-size:clamp(14px,3vh,28px);font-weight:300;letter-spacing:.03em}
/* Name: 2.6%, 22.5% — shows SVG logo, fallback to text */
.cp-sys-name{position:absolute;left:2.6%;top:22.5%;width:30.7%;height:27.5%;z-index:10;display:flex;align-items:flex-start}
.cp-sys-name-logo{max-width:100%;max-height:12vh;object-fit:contain;filter:brightness(0) invert(1) drop-shadow(0 2px 8px rgba(0,0,0,.5))}
.cp-sys-name-text{font-family:'Orbitron',sans-serif;font-size:clamp(22px,5vh,52px);font-weight:900;line-height:1.1}
/* Desc: 2.6%, 44% */
.cp-sys-desc{position:absolute;left:2.6%;top:44%;width:30.7%;height:22%;z-index:10;font-size:clamp(11px,1.6vh,15px);color:rgba(255,255,255,.55);line-height:1.5;overflow-y:auto;scrollbar-width:none}
.cp-sys-desc::-webkit-scrollbar{display:none}

/* Bottom: 3 blocks at 72.2% y, each ~10.4vw x 18.6vh */
.cp-sys-bottom{position:absolute;left:2.55%;top:72.2%;display:flex;z-index:3;gap:0;border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,.08)}
.cp-sys-bottom-block{width:10.4vw;height:18.6vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;backdrop-filter:blur(20px) saturate(150%);-webkit-backdrop-filter:blur(20px) saturate(150%);border-right:1px solid rgba(255,255,255,.06)}
.cp-sys-bottom-block:last-child{border-right:none}
.cp-sys-bottom-block--dark{background:color-mix(in srgb, var(--sys-color) 20%, rgba(0,0,0,.4))}
.cp-sys-bottom-block{background:color-mix(in srgb, var(--sys-color) 15%, rgba(0,0,0,.3))}
.cp-sys-bottom-block--light{background:color-mix(in srgb, var(--sys-color) 10%, rgba(0,0,0,.2))}
.cp-sys-bottom-icon{width:75%;height:auto;max-height:70%;object-fit:contain}
.cp-sys-bottom-icon-color{width:50%;height:auto;max-height:60%;object-fit:contain}
.cp-sys-bottom-fav-icon{height:clamp(28px,4.5vh,44px);width:auto;object-fit:contain;filter:brightness(0) saturate(0) invert(1) sepia(1) hue-rotate(10deg) saturate(5) brightness(1.1)}
.cp-sys-bottom-num{font-family:'Orbitron',sans-serif;font-size:clamp(18px,3vh,32px);font-weight:700}
.cp-sys-bottom-label{font-size:clamp(9px,1.1vh,12px);font-weight:700;text-transform:uppercase;letter-spacing:.12em}

/* Nav arrows: inside right color block, bottom-right corner */

/* ═══ GAME LIST — list-video style ═══════════════════════════════════ */
/* Color panel: 2.6%, 4.6%, 37% wide (list only, not full 56%) */
.cp-gl-panel{position:absolute;left:2.6%;top:4.6%;width:28%;height:90.8%;z-index:1;background:color-mix(in srgb, var(--sys-color) 10%, rgba(0,0,0,.2));backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.05);border-radius:6px}

/* System logo: icon + SVG name, top of list */
.cp-gl-syslogo-wrap{position:absolute;left:5.2%;top:7%;z-index:10;display:flex;align-items:center;gap:10px}
.cp-gl-syslogo-icon{height:clamp(28px,5vh,48px);width:auto}
.cp-gl-syslogo-name{height:clamp(20px,3.5vh,36px);width:auto;max-width:20vw;filter:brightness(0) invert(1)}

/* Text list: just names, rounded pill for selected */
.cp-gl-list{position:absolute;left:5.2%;top:18%;width:22%;height:74%;z-index:10;overflow-y:auto;scrollbar-width:none}
.cp-gl-list::-webkit-scrollbar{display:none}
.cp-gl-row{padding:7px 16px;font-size:clamp(14px,2.2vh,20px);font-weight:700;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-radius:99px;margin-bottom:1px;transition:background .1s}
.cp-gl-row:not(.selected){color:rgba(255,255,255,.45)}
.cp-gl-row.selected{background:rgba(255,255,255,.95);color:var(--sys-color,#4466aa)}
.cp-gl-fav-star{color:#c9a84c;margin-right:4px;font-size:1.1em}
.cp-gl-panel--glass{background:color-mix(in srgb, var(--pl,#00d4ff) 10%, rgba(0,0,0,.2))!important;backdrop-filter:blur(20px) saturate(150%);-webkit-backdrop-filter:blur(20px) saturate(150%);border:1px solid rgba(255,255,255,.06)}
.cp-sys-special-title{font-family:'Orbitron',sans-serif;font-size:clamp(18px,3vh,28px);font-weight:900;color:#fff;text-shadow:0 2px 8px rgba(0,0,0,.5)}

/* Big image on right (like list-video in Pop: screenshot centered in color block area) */
/* Hero background behind cover + overlay area */
.cp-gl-hero{position:absolute;left:30.6%;top:4.5%;right:0;height:91%;z-index:1;overflow:hidden;-webkit-mask-image:linear-gradient(to right,transparent 0%,black 5%,black 95%,transparent 100%);mask-image:linear-gradient(to right,transparent 0%,black 5%,black 95%,transparent 100%)}
.cp-gl-hero-img{position:absolute;inset:-5%;width:110%;height:110%;object-fit:cover;opacity:.25;filter:brightness(.5) saturate(1.2);animation:cp-kenburns 30s ease-in-out infinite alternate}
.cp-gl-hero-img--static{animation:none;inset:0;width:100%;height:100%}
.cp-gl-hero-fade{position:absolute;inset:0;background:linear-gradient(180deg,transparent 50%,var(--bg,#05050f) 100%);z-index:1}

.cp-gl-bigimage{position:absolute;left:3%;top:0;width:28%;height:75%;z-index:2;display:flex;align-items:flex-start;justify-content:center;padding-top:3%;overflow:hidden}
.cp-gl-bigimage-img{max-width:95%;max-height:95%;object-fit:contain;border-radius:4px;box-shadow:0 0 15px var(--sys-color),0 4px 16px rgba(0,0,0,.4)}

/* Overlay + video on right side of game list */
/* IDENTICAL proportions to system view cp-sys-img-wrap (60% x 91%) */
.cp-gl-overlay-wrap{position:absolute;left:42%;top:4.5%;width:60%;height:91%;z-index:5;overflow:hidden}
.cp-gl-overlay-img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;z-index:2;pointer-events:none}
.cp-gl-overlay-video{position:absolute;object-fit:cover;z-index:1}

/* Info panel under cover + overlay */
.cp-gl-info{position:absolute;left:32%;right:4%;top:66%;bottom:5%;z-index:10;display:flex;flex-direction:column;gap:8px;overflow-y:auto;scrollbar-width:none}
.cp-gl-info::-webkit-scrollbar{display:none}
.cp-gl-info-wheel-img{height:clamp(30px,5vh,50px);width:auto;max-width:70%;object-fit:contain}
.cp-gl-info-title{font-family:'Orbitron',sans-serif;font-size:clamp(20px,3.5vh,36px);font-weight:900;line-height:1.1}
.cp-gl-info-meta{display:flex;gap:18px;font-size:clamp(14px,2vh,20px);color:rgba(255,255,255,.5);align-items:center}
.cp-gl-info-rating{font-size:clamp(15px,2.2vh,22px);letter-spacing:1px}
.cp-gl-info-genres{display:flex;gap:8px;flex-wrap:wrap}
.cp-gl-info-genre{padding:3px 12px;border-radius:4px;border:1px solid;font-size:clamp(12px,1.6vh,16px);font-weight:600}
.cp-gl-info-devpub{display:flex;align-items:center;gap:8px;font-size:clamp(14px,1.8vh,18px);color:rgba(255,255,255,.45);flex-wrap:wrap}
.cp-gl-info-company{display:inline-flex;align-items:center;gap:8px}
.cp-gl-info-company-logo{height:clamp(22px,3.5vh,36px);width:auto;max-width:120px;object-fit:contain;filter:brightness(0) invert(1);opacity:.7}
.cp-gl-info-sep{color:rgba(255,255,255,.25)}
.cp-gl-info-desc{font-size:clamp(13px,1.7vh,17px);color:rgba(255,255,255,.55);line-height:1.6;max-height:13vh;overflow-y:auto;scrollbar-width:none;padding:12px 16px;border-radius:6px;background:color-mix(in srgb, var(--sys-color) 10%, rgba(0,0,0,.2));backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.05)}
.cp-gl-info-desc::-webkit-scrollbar{display:none}
.cp-gl-info-hltb{display:flex;gap:16px;font-size:clamp(13px,1.6vh,16px);color:rgba(255,255,255,.4)}

/* ═══ GAME CAROUSEL — full-screen artwork ════════════════════════════ */
.cp-gc-bg{position:absolute;inset:0;z-index:0}
.cp-gc-bg-img{width:100%;height:100%;object-fit:cover;filter:brightness(.5)}
.cp-gc-dim{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(0,0,0,.2) 0%,rgba(0,0,0,.1) 50%,rgba(0,0,0,.7) 100%)}

/* System name: top left */
.cp-gc-sysname{position:absolute;left:2.6%;top:4.6%;z-index:10;font-family:'Orbitron',sans-serif;font-size:clamp(12px,2vh,20px);font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.5)}
/* Game name: bottom left, BIG */
.cp-gc-gamename{position:absolute;left:2.6%;bottom:16%;width:40%;z-index:10;font-family:'Orbitron',sans-serif;font-size:clamp(28px,6vh,64px);font-weight:900;line-height:1.05;text-shadow:0 2px 16px rgba(0,0,0,.8)}
/* Year: below game name */
.cp-gc-year{position:absolute;left:2.6%;bottom:10%;z-index:10;font-size:clamp(12px,1.8vh,16px);color:rgba(255,255,255,.4)}

/* ═══ HELP BAR ════════════════════════════════════════════════════ */
.cp-help{position:absolute;bottom:0;left:0;right:0;z-index:50;padding:12px 0;display:flex;gap:32px;justify-content:center;font-size:16px;color:rgba(255,255,255,.4);letter-spacing:.02em;align-items:center}
.cp-help-item{display:inline-flex;align-items:center;gap:8px}
.cp-help-icon{width:28px;height:28px;flex-shrink:0}
.cp-help-btn{width:30px;height:30px}
.cp-help-btn-wide{width:48px;height:28px}

/* ═══ OVERLAYS ════════════════════════════════════════════════════ */
.cp-overlay{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.75);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center}
.cp-menu{width:340px;background:rgba(20,16,40,.97);border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:20px 16px}
.cp-menu-title{font-family:'Orbitron';font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:10px}
.cp-menu-row{padding:10px 14px;border-radius:8px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);margin-bottom:4px;font-size:14px;font-weight:600;color:rgba(255,255,255,.6);cursor:pointer;transition:all .1s}
.cp-menu-row.focus{background:rgba(255,255,255,.1);border-color:var(--sys-color);color:#fff}
.cp-menu-row.danger{color:#ef4444}
.cp-menu-row.danger.focus{background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.35)}

.cp-shot-img{max-width:90vw;max-height:85vh;object-fit:contain;border-radius:6px}
.cp-shot-ctr{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);font-family:'Orbitron';font-size:12px;color:rgba(255,255,255,.4)}

/* ═══ MENU TABS ══════════════════════════════════════════════════════ */
.cp-menu-tabs{display:flex;gap:0;margin-bottom:10px;border-bottom:1px solid rgba(255,255,255,.1)}
.cp-menu-tab{flex:1;padding:8px 0;background:none;border:none;border-bottom:2px solid transparent;color:rgba(255,255,255,.35);font-family:'Orbitron',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;transition:all .15s}
.cp-menu-tab:hover{color:rgba(255,255,255,.6)}
.cp-menu-tab.active{color:var(--sys-color,#4466aa);border-bottom-color:var(--sys-color,#4466aa)}

/* ═══ ICON ANIMATIONS ════════════════════════════════════════════════ */
.cp-icon-anim--shake{animation:cp-shake 8s ease-in-out infinite}
.cp-icon-anim--spin{animation:cp-spin 8s ease-in-out infinite}
.cp-icon-anim--pop{animation:cp-pop 8s ease-in-out infinite}
.cp-icon-anim--bounce{animation:cp-bounce-icon 8s ease-in-out infinite}

/* Sporadic = long pause, short burst. 8s total, action only in first 15% */
@keyframes cp-shake{0%,100%{transform:rotate(0)}2%{transform:rotate(-12deg)}4%{transform:rotate(10deg)}6%{transform:rotate(-8deg)}8%{transform:rotate(5deg)}10%{transform:rotate(0)}}
@keyframes cp-spin{0%{transform:rotate(0)}12%{transform:rotate(360deg)}100%{transform:rotate(360deg)}}
@keyframes cp-pop{0%,100%{transform:scale(1)}3%{transform:scale(1.3)}6%{transform:scale(0.85)}9%{transform:scale(1.15)}12%{transform:scale(1)}}
@keyframes cp-bounce-icon{0%,100%{transform:translateY(0)}4%{transform:translateY(-20%)}8%{transform:translateY(0)}11%{transform:translateY(-10%)}14%{transform:translateY(0)}}
</style>
