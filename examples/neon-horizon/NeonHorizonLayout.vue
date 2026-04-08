<template>
  <div class="nh-shell" :class="{ 'nh-no-anim': !themeStore.animations }">
    <!-- ── Animated gradient background ─────────────────────────────────── -->
    <div v-if="themeStore.ambient" class="nh-bg-gradient" />

    <!-- ── Floating particles ───────────────────────────────────────────── -->
    <div v-if="themeStore.animations && particleCount > 0" class="nh-particles">
      <div
        v-for="i in particleCount"
        :key="i"
        class="nh-particle"
        :style="{
          left: (5 + ((i * 13 + 7) % 85)) + '%',
          animationDuration: (8 + (i * 1.3) % 6) + 's',
          animationDelay: (i * 1.2) + 's',
          width: (1.5 + (i % 3)) + 'px',
          height: (1.5 + (i % 3)) + 'px',
        }"
      />
    </div>

    <!-- ── Navbar ────────────────────────────────────────────────────────── -->
    <nav class="nh-navbar">
      <router-link to="/" class="nh-logo">
        <img src="/GDLOGO.png" class="nh-logo-img" alt="" />
      </router-link>

      <div class="nh-nav-tabs">
        <router-link to="/" class="nh-tab" :class="{ active: isHomePage }">Home</router-link>
        <router-link v-if="isAdmin" to="/library" class="nh-tab" :class="{ active: isRouteActive('/library') }">GOG Library</router-link>
        <router-link to="/games" class="nh-tab" :class="{ active: isRouteActive('/games') }">Games Library</router-link>
        <router-link to="/emulation" class="nh-tab" :class="{ active: isRouteActive('/emulation') }">Emulation</router-link>
      </div>

      <div class="nh-nav-center">
        <div class="nh-search" :class="{ focused: searchFocused }">
          <svg class="nh-search-ico" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
          <input
            v-model="searchQuery"
            class="nh-search-input"
            placeholder="Search games…"
            @focus="searchFocused = true"
            @blur="searchFocused = false"
          />
          <button v-if="searchQuery" class="nh-search-clear" @click="searchQuery = ''">×</button>
        </div>
        <RandomGamePicker />
      </div>

      <div class="nh-nav-right">
        <div class="nh-user-wrap" @click="showUserMenu = !showUserMenu" v-click-outside="() => showUserMenu = false">
          <div class="nh-user-chip">
            <img v-if="avatarSrc" :src="avatarSrc" class="nh-avatar-img" alt="" @error="(e) => (e.target as HTMLImageElement).style.display='none'" />
            <div v-else class="nh-avatar-ph">{{ initials }}</div>
          </div>
          <transition name="nh-menu-drop">
            <div v-if="showUserMenu" class="nh-user-menu">
              <div class="nh-menu-header">
                <div class="nh-menu-avatar">
                  <img v-if="avatarSrc" :src="avatarSrc" class="nh-avatar-img" alt="" @error="(e) => (e.target as HTMLImageElement).style.display='none'" />
                  <div v-else class="nh-avatar-ph small">{{ initials }}</div>
                </div>
                <div>
                  <div class="nh-menu-name">{{ auth.user?.username || 'User' }}</div>
                  <div class="nh-menu-role">{{ userRole }}</div>
                </div>
              </div>
              <div class="nh-menu-sep" />
              <button class="nh-menu-item" @click="showUserMenu = false; $router.push('/profile')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                Profile
              </button>
              <button class="nh-menu-item" @click="showUserMenu = false; $router.push('/settings')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                Settings
              </button>
              <div class="nh-menu-sep" />
              <button class="nh-menu-item nh-menu-item--danger" @click="handleLogout">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                Log out
              </button>
            </div>
          </transition>
        </div>
      </div>
    </nav>

    <!-- ── Sync progress ────────────────────────────────────────────────── -->
    <div v-if="socketStore.syncProgress.progress > 0 && socketStore.syncProgress.progress < 100" class="nh-sync-bar">
      <div class="nh-sync-fill" :style="{ width: socketStore.syncProgress.progress + '%' }" />
    </div>

    <!-- ── Main content ─────────────────────────────────────────────────── -->
    <main class="nh-main" :class="{ 'nh-main--full': $route.meta.fullBleed }">
      <!-- Global search — takes over entire content when query is active -->
      <NeonHorizonSearch v-if="searchQuery" :query="searchQuery" :key="'search-'+searchQuery" />
      <!-- Custom home page -->
      <NeonHorizonHome v-else-if="isHomePage" />
      <!-- Custom library views (GOG, Games, Emulation) -->
      <NeonHorizonLibrary v-else-if="isNhLibraryView" :key="$route.path" />
      <!-- All other pages (detail, profile, settings) use standard router-view -->
      <router-view v-else v-slot="{ Component }">
        <template v-if="$route.meta.fullBleed">
          <component :is="Component" :key="$route.path" />
        </template>
        <transition v-else name="nh-page">
          <component :is="Component" :key="$route.path" />
        </transition>
      </router-view>
    </main>
  </div>

  <DownloadManager v-if="isAdmin" />
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import NeonHorizonHome from "./NeonHorizonHome.vue";
import NeonHorizonLibrary from "./NeonHorizonLibrary.vue";
import NeonHorizonSearch from "./NeonHorizonSearch.vue";

// Use GD plugin API for stores (not compiled into plugin bundle)
const _gd = (window as any).__GD__;
const auth = _gd.stores.auth();
const socketStore = _gd.stores.socket();
const themeStore = _gd.stores.theme();

// Read particle count from theme settings (plugin.py declares 'particleCount' setting)
const particleCount = computed(() => {
  const val = themeStore.getThemeSettingValue('particleCount')
  return Number(val) || 6
});
const router = useRouter();
const route  = useRoute();

const searchQuery = ref("");
const searchFocused = ref(false);
const showUserMenu = ref(false);

const initials = computed(() => {
  const name = (auth.user?.username as string) || "?";
  return name.slice(0, 2).toUpperCase();
});

const avatarSrc = computed(() => {
  const p = auth.user?.avatar_path as string | undefined;
  if (!p) return '';
  if (p.startsWith('http')) return p;
  const filename = p.split(/[\\/]/).pop() || '';
  return filename ? `/resources/avatars/${filename}` : '';
});

const userRole = computed(() => {
  const r = (auth.user?.role as string) || 'viewer';
  return r.charAt(0).toUpperCase() + r.slice(1).toLowerCase();
});

const isAdmin = computed(() => auth.user?.role === 'admin');
const isHomePage = computed(() => route.path === '/' || route.path === '/home');

// Library routes: show NeonHorizonLibrary instead of default GD views
// Matches: /library, /games, /emulation, /emulation/:platform
// Does NOT match: /library/:id (detail), /games/:id, /emulation/:platform/:id
const isNhLibraryView = computed(() => {
  const p = route.path;
  if (p === '/library' || p === '/games' || p === '/emulation') return true;
  if (p.startsWith('/emulation/') && !p.match(/^\/emulation\/[^/]+\/\d/)) return true;
  return false;
});

function isRouteActive(prefix: string): boolean {
  return route.path === prefix || route.path.startsWith(prefix + '/');
}

// Search sync — works on ALL routes (NH search is global)
watch(searchQuery, (q) => {
  const cur = Array.isArray(route.query.q) ? route.query.q[0] : route.query.q;
  if (q !== (cur || "")) {
    router.replace({ query: { ...route.query, q: q || undefined } });
  }
});

watch(() => route.query.q, (q) => {
  const val = (Array.isArray(q) ? q[0] : q) || "";
  if (searchQuery.value !== val) searchQuery.value = val;
}, { immediate: true });

function handleLogout() {
  showUserMenu.value = false;
  auth.logout();
  router.push("/login");
}

socketStore.connect();

type ElWithHandler = HTMLElement & { _clickOutside?: (e: Event) => void }
const vClickOutside = {
  mounted(el: ElWithHandler, binding: { value: () => void }) {
    el._clickOutside = (e: Event) => {
      if (!el.contains(e.target as Node)) binding.value();
    };
    document.addEventListener("click", el._clickOutside);
  },
  unmounted(el: ElWithHandler) {
    if (el._clickOutside) document.removeEventListener("click", el._clickOutside);
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

/* ═══════════════════════════════════════════════════════════════════════════
   SHELL
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: var(--bg, #05050f);
  font-family: 'Rajdhani', sans-serif;
  color: var(--text, #e0e6ff);
}

/* ═══════════════════════════════════════════════════════════════════════════
   ANIMATED GRADIENT BACKGROUND
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-bg-gradient {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 80% 60% at 20% 80%, var(--pglow2, rgba(123,47,255,.2)) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 20%, var(--pglow, rgba(0,212,255,.15)) 0%, transparent 50%);
  animation: nh-bg-shift 20s ease-in-out infinite alternate;
}

@keyframes nh-bg-shift {
  0%   { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(30deg); }
}

/* ═══════════════════════════════════════════════════════════════════════════
   FLOATING PARTICLES
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-particles {
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
}

.nh-particle {
  position: absolute;
  bottom: -10px;
  background: var(--pl, #00d4ff);
  border-radius: 50%;
  opacity: 0;
  animation: nh-float-up 10s ease-in infinite;
  box-shadow: 0 0 6px var(--pglow, rgba(0,212,255,.4));
}

@keyframes nh-float-up {
  0%   { transform: translateY(0) scale(0); opacity: 0; }
  10%  { opacity: .6; }
  50%  { opacity: .3; }
  90%  { opacity: .1; }
  100% { transform: translateY(-110vh) scale(1.5); opacity: 0; }
}

/* ═══════════════════════════════════════════════════════════════════════════
   NAVBAR — exactly matching theme-preview.html nav-tabs style
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-navbar {
  display: flex;
  align-items: stretch;
  padding: 0 20px;
  gap: 0;
  flex-shrink: 0;
  z-index: 100;
  position: relative;
  background: rgba(5, 5, 15, .9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--glass-border, rgba(0,212,255,.12));
}

.nh-logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  flex-shrink: 0;
  padding: 0 8px 0 0;
}

/* ── Library tabs ─────────────────────────────────────────────────────── */
.nh-nav-tabs {
  display: flex;
  align-items: stretch;
  gap: 0;
}

.nh-tab {
  display: flex;
  align-items: center;
  padding: 14px 24px;
  font-family: 'Orbitron', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--muted);
  border-bottom: 2px solid transparent;
  transition: all .2s;
  white-space: nowrap;
  cursor: pointer;
}

.nh-tab:hover {
  color: var(--text);
}

.nh-tab.active {
  color: var(--pl);
  border-bottom-color: var(--pl);
  text-shadow: 0 0 12px var(--pglow, rgba(0,212,255,.4));
}

.nh-logo-img {
  height: 36px;
  width: auto;
  filter: drop-shadow(0 0 12px var(--pglow, rgba(0,212,255,.4)));
  transition: filter .2s;
}

.nh-logo:hover .nh-logo-img {
  filter: drop-shadow(0 0 20px var(--pglow, rgba(0,212,255,.4)))
          drop-shadow(0 0 40px var(--pglow2, rgba(0,212,255,.2)));
}

/* Search */
.nh-nav-center {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  padding: 0 12px;
}

.nh-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 8px;
  background: rgba(255,255,255,.05);
  transition: all .2s;
  width: 340px;
}

.nh-search.focused {
  border-color: var(--pl);
  background: rgba(255,255,255,.08);
  box-shadow: 0 0 16px var(--pglow2, rgba(0,212,255,.2));
}

.nh-search-ico { color: var(--muted); flex-shrink: 0; }
.nh-search-input {
  flex: 1;
  font-size: 13px;
  font-family: 'Rajdhani', sans-serif;
  color: var(--text);
  background: none;
  border: none;
  outline: none;
}
.nh-search-input::placeholder { color: var(--muted); }
.nh-search-clear {
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 16px;
  padding: 0 2px;
}

/* Right */
.nh-nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* User chip */
.nh-user-wrap { position: relative; }
.nh-user-chip {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 2px solid var(--pl);
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 0 10px var(--pglow2);
  transition: all .15s;
}
.nh-user-chip:hover {
  box-shadow: 0 0 16px var(--pglow);
  transform: scale(1.05);
}
.nh-avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; display: block; }
.nh-avatar-ph {
  display: flex; align-items: center; justify-content: center;
  width: 100%; height: 100%;
  background: linear-gradient(135deg, var(--pl), var(--pl2, var(--pl)));
  font-family: 'Orbitron', sans-serif;
  font-size: 12px; font-weight: 700; color: #fff;
}
.nh-avatar-ph.small { width: 32px; height: 32px; border-radius: 50%; font-size: 11px; }

/* User dropdown menu */
.nh-user-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 200px;
  background: rgba(10, 6, 24, .97);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border, rgba(0,212,255,.12));
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 0 40px var(--pglow2, rgba(0,212,255,.2)), 0 16px 48px rgba(0,0,0,.6);
  z-index: 200;
}
.nh-menu-header {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 16px;
  background: rgba(0,212,255,.06);
}
.nh-menu-avatar { width: 32px; height: 32px; border-radius: 50%; overflow: hidden; flex-shrink: 0; border: 1px solid var(--glass-border); }
.nh-menu-name { font-family: 'Orbitron', sans-serif; font-size: 12px; font-weight: 700; color: var(--text); }
.nh-menu-role { font-size: 11px; color: var(--muted); text-transform: capitalize; }
.nh-menu-sep { height: 1px; background: var(--glass-border); margin: 2px 0; }
.nh-menu-item {
  display: flex; align-items: center; gap: 9px;
  padding: 11px 16px; font-size: 13px; font-weight: 600;
  font-family: 'Rajdhani', sans-serif;
  color: var(--text); background: none; border: none;
  width: 100%; cursor: pointer; transition: background .15s;
}
.nh-menu-item:hover { background: rgba(255,255,255,.06); }
.nh-menu-item--danger { color: var(--danger, #ef4444); }
.nh-menu-item--danger:hover { background: rgba(239,68,68,.08); }

.nh-menu-drop-enter-active { animation: nh-menu-in .15s ease; }
.nh-menu-drop-leave-active { animation: nh-menu-in .1s ease reverse; }
@keyframes nh-menu-in {
  from { opacity: 0; transform: translateY(-6px) scale(.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ═══════════════════════════════════════════════════════════════════════════
   SYNC PROGRESS BAR
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-sync-bar {
  height: 2px;
  background: rgba(0,212,255,.1);
  flex-shrink: 0;
}
.nh-sync-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--pl), var(--pl2, var(--pl)));
  box-shadow: 0 0 8px var(--pglow);
  transition: width .3s ease;
}

/* ═══════════════════════════════════════════════════════════════════════════
   MAIN CONTENT
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-main {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  z-index: 2;
  padding: 20px 28px;
  position: relative;
}
.nh-main--full { padding: 0; }

/* Page transition */
.nh-page-enter-active { animation: nh-page-in .25s ease; }
.nh-page-leave-active { animation: nh-page-in .15s ease reverse; }
@keyframes nh-page-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════════════════════════════════════════════════════════════
   ANIMATIONS DISABLED
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-no-anim,
.nh-no-anim * {
  animation-duration: 0s !important;
  animation-delay: 0s !important;
  transition-duration: 0s !important;
}
.nh-no-anim .nh-bg-gradient { animation: none !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════════════════════ */
.nh-main::-webkit-scrollbar { width: 6px; }
.nh-main::-webkit-scrollbar-track { background: transparent; }
.nh-main::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb, rgba(0,212,255,.3)); border-radius: 3px; }
.nh-main::-webkit-scrollbar-thumb:hover { background: var(--pl); }

/* ═══════════════════════════════════════════════════════════════════════════
   MOBILE
   ═══════════════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .nh-navbar {
    height: auto;
    padding: 8px 12px;
    flex-wrap: wrap;
    gap: 0;
  }
  .nh-logo-img { height: 28px; }
  .nh-nav-tabs {
    overflow-x: auto;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
  }
  .nh-nav-tabs::-webkit-scrollbar { display: none; }
  .nh-tab {
    font-size: 10px;
    padding: 10px 12px;
  }
  .nh-nav-center {
    width: 100%;
    order: 3;
    flex-basis: 100%;
    padding: 6px 0;
    margin-left: 0;
  }
  .nh-search { width: 100%; }
  .nh-main { padding: 10px 12px; }
  .nh-particles { display: none; }
}
</style>
