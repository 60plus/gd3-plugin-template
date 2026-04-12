<template>
  <div class="nh-search-results">
    <div class="nh-sr-header">
      <span class="nh-sr-label">{{ t('nh.search_results_for') }}</span>
      <span class="nh-sr-query">"{{ query }}"</span>
      <span class="nh-sr-total">{{ t('nh.found', { count: totalResults }) }}</span>
    </div>

    <!-- GOG results -->
    <section v-if="gogResults.length" class="nh-sr-section">
      <div class="nh-sr-section-head">
        <span class="nh-sr-section-title">{{ t('nh.library_gog') }}</span>
        <span class="nh-sr-section-count">{{ gogResults.length }}</span>
      </div>
      <div class="nh-sr-grid">
        <div v-for="g in gogResults" :key="'gog-'+g.id" class="nh-bp-card" @click="openGog(g)">
          <div class="nh-bp-bg">
            <img v-if="g.background_path || gogCover(g)" :src="g.background_path || gogCover(g)" class="nh-bp-bg-img" loading="lazy" />
            <div v-else class="nh-bp-bg-fallback" />
          </div>
          <div class="nh-bp-gradient" />
          <img v-if="gogCover(g) && g.background_path" :src="gogCover(g)" class="nh-bp-thumb" loading="lazy" />
          <div class="nh-bp-info">
            <div class="nh-bp-title">{{ g.title }}</div>
            <div v-if="g.developer" class="nh-bp-meta">{{ g.developer }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Games Library results -->
    <section v-if="gamesResults.length" class="nh-sr-section">
      <div class="nh-sr-section-head">
        <span class="nh-sr-section-title">{{ t('nh.library_games') }}</span>
        <span class="nh-sr-section-count">{{ gamesResults.length }}</span>
      </div>
      <div class="nh-sr-grid">
        <div v-for="g in gamesResults" :key="'lib-'+g.id" class="nh-bp-card" @click="openGame(g)">
          <div class="nh-bp-bg">
            <img v-if="g.background_path || g.cover_path" :src="g.background_path || g.cover_path" class="nh-bp-bg-img" loading="lazy" />
            <div v-else class="nh-bp-bg-fallback" />
          </div>
          <div class="nh-bp-gradient" />
          <img v-if="g.cover_path && g.background_path" :src="g.cover_path" class="nh-bp-thumb" loading="lazy" />
          <div class="nh-bp-info">
            <div class="nh-bp-title">{{ g.title }}</div>
            <div v-if="g.developer" class="nh-bp-meta">{{ g.developer }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Emulation results -->
    <section v-if="emuResults.length" class="nh-sr-section">
      <div class="nh-sr-section-head">
        <span class="nh-sr-section-title">{{ t('nh.library_emulation') }}</span>
        <span class="nh-sr-section-count">{{ emuResults.length }}</span>
      </div>
      <div class="nh-sr-grid">
        <div v-for="r in emuResults" :key="'rom-'+r.id" class="nh-bp-card" @click="openRom(r)">
          <div class="nh-bp-bg">
            <img v-if="r.cover_path" :src="r.cover_path" class="nh-bp-bg-img" loading="lazy" />
            <div v-else class="nh-bp-bg-fallback" />
          </div>
          <div class="nh-bp-gradient" />
          <div class="nh-bp-info">
            <div class="nh-bp-title">{{ r.name }}</div>
            <div v-if="r.platform_name" class="nh-bp-meta">{{ r.platform_name }}</div>
          </div>
        </div>
      </div>
    </section>

    <div v-if="!loading && totalResults === 0" class="nh-sr-empty">
      <div class="nh-sr-empty-text">{{ t('nh.no_results') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps<{ query: string }>()

const _gd = (window as any).__GD__
const client = _gd.api
const t = _gd.i18n?.t || ((k: string) => k)
const auth = _gd.stores.auth()
const router = useRouter()

const loading = ref(false)
const allGog = ref<any[]>([])
const allGames = ref<any[]>([])
const allRoms = ref<any[]>([])
const dataLoaded = ref(false)

const isAdmin = computed(() => auth.user?.role === 'admin')

const _GOG_RE = /(_product_card|_logo2x?|_icon|_square_icon|_196|_200|_bg_crop_\d+x\d+)(\.\w+)?$/i
function gogCover(g: any): string {
  if (g.cover_path) return g.cover_path
  const url = g.cover_url || ''
  if (!url) return ''
  const fixed = url.replace(_GOG_RE, '')
  return /\.\w{2,5}(\?|$)/.test(fixed) ? fixed : fixed + '.jpg'
}

const gogResults = computed(() => {
  if (!isAdmin.value) return []
  const q = props.query.toLowerCase()
  return allGog.value.filter(g => (g.title || '').toLowerCase().includes(q)).slice(0, 20)
})

const gamesResults = computed(() => {
  const q = props.query.toLowerCase()
  return allGames.value.filter(g => (g.title || '').toLowerCase().includes(q)).slice(0, 20)
})

const emuResults = computed(() => {
  const q = props.query.toLowerCase()
  return allRoms.value.filter(r => (r.name || '').toLowerCase().includes(q)).slice(0, 20)
})

const totalResults = computed(() => gogResults.value.length + gamesResults.value.length + emuResults.value.length)

async function loadAll() {
  if (dataLoaded.value) return
  loading.value = true
  const [gogRes, gamesRes, romsRes] = await Promise.allSettled([
    isAdmin.value ? client.get('/gog/library/games') : Promise.resolve({ data: [] }),
    client.get('/library/games', { params: { limit: '2000' } }),
    client.get('/roms/recent', { params: { limit: 48 } }),
  ])
  if (gogRes.status === 'fulfilled') {
    const raw = gogRes.value.data
    allGog.value = Array.isArray(raw) ? raw : raw.items ?? []
  }
  if (gamesRes.status === 'fulfilled') allGames.value = gamesRes.value.data.items ?? []
  if (romsRes.status === 'fulfilled') allRoms.value = Array.isArray(romsRes.value.data) ? romsRes.value.data : []
  dataLoaded.value = true
  loading.value = false
}

function openGog(g: any) { router.push({ name: 'game-detail', params: { id: g.id } }) }
function openGame(g: any) { router.push({ name: 'games-detail', params: { id: g.id } }) }
function openRom(r: any) { if (r.platform_slug) router.push({ name: 'emulation-detail', params: { platform: r.platform_slug, id: r.id } }) }

onMounted(loadAll)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

.nh-search-results { padding: 0 28px 48px; }

.nh-sr-header {
  display: flex; align-items: baseline; gap: 10px; padding: 16px 0 20px;
  border-bottom: 1px solid var(--glass-border, rgba(0,212,255,.12)); margin-bottom: 24px;
}
.nh-sr-label { font-family: 'Orbitron', sans-serif; font-size: 10px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.nh-sr-query { font-family: 'Orbitron', sans-serif; font-size: 16px; font-weight: 900; color: var(--pl); }
.nh-sr-total { font-family: 'Orbitron', sans-serif; font-size: 10px; font-weight: 700; color: var(--muted); margin-left: auto; }

.nh-sr-section { margin-bottom: 32px; }
.nh-sr-section-head { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.nh-sr-section-title { font-family: 'Orbitron', sans-serif; font-size: 10px; font-weight: 700; letter-spacing: .15em; text-transform: uppercase; color: var(--pl); }
.nh-sr-section-count { font-family: 'Orbitron', sans-serif; font-size: 9px; font-weight: 700; padding: 2px 8px; border-radius: 3px; background: var(--pl-dim, rgba(0,212,255,.1)); color: var(--pl); }

.nh-sr-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px;
}

/* Reuse Big Picture card styles */
.nh-bp-card { position: relative; aspect-ratio: 16/9; border-radius: 6px; overflow: hidden; cursor: pointer; border: 1px solid rgba(255,255,255,.06); transition: all .35s cubic-bezier(.25,.46,.45,.94); }
.nh-bp-card:hover { transform: translateY(-6px) scale(1.02); border-color: var(--pl); box-shadow: 0 24px 60px rgba(0,0,0,.7), 0 0 30px var(--pglow2, rgba(0,212,255,.2)); z-index: 2; }
.nh-bp-bg { position: absolute; inset: -4px; }
.nh-bp-bg-img { width: calc(100% + 8px); height: calc(100% + 8px); object-fit: cover; filter: brightness(.55) saturate(1.2); transition: all .4s; }
.nh-bp-card:hover .nh-bp-bg-img { filter: brightness(.7) saturate(1.3); transform: scale(1.04); }
.nh-bp-bg-fallback { position: absolute; inset: 0; background: linear-gradient(135deg, var(--bg2, #0a0a1a), var(--bg3, #0f0f25)); }
.nh-bp-gradient { position: absolute; inset: 0; background: linear-gradient(180deg, transparent 30%, rgba(5,5,15,.5) 60%, rgba(5,5,15,.92) 100%); z-index: 1; }
.nh-bp-thumb { position: absolute; top: 10px; left: 10px; width: 40px; height: 54px; object-fit: cover; border-radius: 4px; border: 1px solid rgba(255,255,255,.15); box-shadow: 0 4px 16px rgba(0,0,0,.6); z-index: 2; opacity: .85; }
.nh-bp-info { position: absolute; bottom: 0; left: 0; right: 0; padding: 14px; z-index: 2; }
.nh-bp-title { font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 900; color: #fff; text-shadow: 0 2px 8px rgba(0,0,0,.8); line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.nh-bp-meta { font-family: 'Rajdhani', sans-serif; font-size: 11px; color: rgba(255,255,255,.5); margin-top: 3px; }

.nh-sr-empty { display: flex; align-items: center; justify-content: center; padding: 80px 20px; }
.nh-sr-empty-text { font-family: 'Orbitron', sans-serif; font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }

@media (max-width: 768px) {
  .nh-search-results { padding: 0 12px 32px; }
  .nh-sr-grid { grid-template-columns: 1fr; }
}
</style>
