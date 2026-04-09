<template>
  <div class="cp" :style="{ '--sys-color': sysColor, '--bg': '#1e1e2e' }">

    <!-- ═══ SYSTEM VIEW — Colorful Pop exact ═══════════════════════════ -->
    <template v-if="state === 'systems'">
      <div class="cp-bg" />

      <!-- Right color block (35.9% from left, 61.5% wide, 91% tall) -->
      <div class="cp-sys-block" :style="{ backgroundColor: sysColor }" />

      <!-- Platform image: centered in right block -->
      <div class="cp-sys-img-wrap">
        <transition name="cp-slide" mode="out-in">
          <img v-if="currentPlatform" :key="currentPlatform.fs_slug" :src="'/platforms/fanart/' + currentPlatform.fs_slug + '.webp'" class="cp-sys-img" @error="(e:any) => e.target.src='/platforms/fanart/_default.webp'" />
        </transition>
      </div>

      <!-- Year -->
      <div class="cp-sys-year" :style="{ color: sysColor }">{{ currentPlatform?.release_year_platform || '' }}</div>
      <!-- Platform name -->
      <div class="cp-sys-name">{{ currentPlatform?.name || '' }}</div>
      <!-- Description -->
      <div class="cp-sys-desc">{{ currentPlatform?.description || '' }}</div>

      <!-- Bottom: 3 color blocks + icon + counts (like Pop) -->
      <div class="cp-sys-bottom">
        <div class="cp-sys-bottom-block cp-sys-bottom-block--dark" :style="{ backgroundColor: sysColor }">
          <img :src="'/platforms/icons/' + (currentPlatform?.fs_slug||'') + '.png'" class="cp-sys-bottom-icon" @error="(e:any) => e.target.style.display='none'" />
        </div>
        <div class="cp-sys-bottom-block" :style="{ backgroundColor: sysColor }">
          <div class="cp-sys-bottom-num">{{ currentPlatform?.rom_count || 0 }}</div>
          <div class="cp-sys-bottom-label">GAMES</div>
        </div>
        <div class="cp-sys-bottom-block cp-sys-bottom-block--light" :style="{ backgroundColor: sysColor }" />
      </div>

      <!-- Nav arrows (white boxes, bottom right) -->
      <div class="cp-sys-arrows">
        <button class="cp-sys-arrow" @click="goSys(-1)">▲</button>
        <button class="cp-sys-arrow" @click="goSys(1)">▼</button>
      </div>

      <div class="cp-help">
        <span>↑↓ Navigate</span>
        <span>A Select</span>
        <span>Start Menu</span>
        <span>B Back</span>
      </div>
    </template>

    <!-- ═══ GAME LIST — list-video (Pop style: text list + big image) ══ -->
    <template v-if="state === 'games-list'">
      <div class="cp-bg" />
      <!-- Colored panel behind list -->
      <div class="cp-gl-panel" :style="{ backgroundColor: sysColor }" />

      <!-- System logo (top, above list) -->
      <div class="cp-gl-syslogo-wrap">
        <img :src="'/platforms/icons/' + (currentPlatform?.fs_slug||'') + '.png'" class="cp-gl-syslogo-icon" @error="(e:any) => e.target.style.display='none'" />
        <img :src="'/platforms/names/' + (currentPlatform?.fs_slug||'') + '.svg'" class="cp-gl-syslogo-name" @error="(e:any) => e.target.style.display='none'" />
      </div>

      <!-- Text list (just names, no covers — like Pop) -->
      <div class="cp-gl-list" ref="gameListRef">
        <div
          v-for="(rom, i) in roms" :key="rom.id"
          class="cp-gl-row"
          :class="{ selected: i === romIdx }"
          @click="romIdx = i"
        >{{ rom.title }}</div>
      </div>

      <!-- Big image: screenshot/video/cover (center-right, 60% x 91%) -->
      <div class="cp-gl-bigimage">
        <img v-if="detail?.screenshots?.[0]" :src="detail.screenshots[0]" class="cp-gl-bigimage-img" />
        <img v-else-if="selectedRom?.cover_path" :src="selectedRom.cover_path" class="cp-gl-bigimage-img" />
      </div>

      <div class="cp-help">
        <span>↑↓ Games</span>
        <span>A Play</span>
        <span>X Screenshots</span>
        <span>Tab View</span>
        <span>B Back</span>
      </div>
    </template>

    <!-- ═══ GAME CAROUSEL — full-screen fanart (Pop style) ═════════════ -->
    <template v-if="state === 'games-carousel'">
      <!-- Full-screen game artwork -->
      <div class="cp-gc-bg">
        <transition name="cp-slide" mode="out-in">
          <img v-if="selectedRom" :key="selectedRom.id" :src="selectedRom.background_path || selectedRom.cover_path || ''" class="cp-gc-bg-img" />
        </transition>
      </div>
      <div class="cp-gc-dim" />

      <!-- System name (top left) -->
      <div class="cp-gc-sysname">{{ currentPlatform?.name || '' }}</div>

      <!-- Game name (bottom left, big) -->
      <div class="cp-gc-gamename">{{ selectedRom?.title || '' }}</div>

      <!-- Year (bottom left, small) -->
      <div class="cp-gc-year">{{ selectedRom?.release_year || '' }}</div>

      <div class="cp-help">
        <span>←→ Games</span>
        <span>A Play</span>
        <span>B Back</span>
        <span>Start Menu</span>
      </div>
    </template>

    <!-- ═══ OVERLAYS ═══════════════════════════════════════════════════ -->
    <transition name="cp-fade">
      <div v-if="menuOpen" class="cp-overlay" @click.self="menuOpen=false">
        <div class="cp-menu">
          <div class="cp-menu-title" :style="{color:sysColor}">SETTINGS</div>
          <div v-for="(m,i) in menuItems" :key="i" class="cp-menu-row" :class="{focus:menuIdx===i,danger:m.danger}" @click="m.action">{{m.label}}</div>
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
interface Detail { description:string|null; screenshots:string[]|null; developer:string|null; genres:string[]|null; ss_score:number|null; wheel_path:string|null }

const COLORS: Record<string,string> = {
  nes:'#c43d41',snes:'#df5142',n64:'#367d3f',gb:'#5a6e7e',gba:'#3f3f95',gbc:'#6b3fa0',
  nds:'#a0a0a0',genesis:'#c23b2c',megadrive:'#c23b2c',mastersystem:'#bf2020',gamegear:'#2c68b0',
  saturn:'#5566aa',dreamcast:'#e87d2a',psx:'#2555a0',psp:'#444444',neogeo:'#d4a935',
  arcade:'#e8b230',atarist:'#3a7bc8',atari2600:'#c85a30',fbneo:'#e8b230',mame:'#e8b230',
  pc:'#3daee8',windows:'#3daee8',
}

type State = 'systems'|'games-list'|'games-carousel'
const state = ref<State>('systems')
const platforms = ref<Platform[]>([])
const sysIdx = ref(0)
const roms = ref<Rom[]>([])
const romIdx = ref(0)
const detail = ref<Detail|null>(null)
const cache = new Map<number,Detail>()
const gameView = ref<'list'|'carousel'>(localStorage.getItem('gd3_couch_view') as any||'list')
const menuOpen = ref(false); const menuIdx = ref(0)
const exitOpen = ref(false); const exitIdx = ref(0)
const shotIdx = ref(-1)
const gameListRef = ref<HTMLElement|null>(null)
const loaded = new Set<string>()
const launchMode = ref(localStorage.getItem('gd3_couch_launch')||'tab')
const bezelOn = ref(localStorage.getItem('gd3_couch_bezel')==='on')

const currentPlatform = computed(()=>platforms.value[sysIdx.value]??null)
const selectedRom = computed(()=>roms.value[romIdx.value]??null)
const sysColor = computed(()=>COLORS[currentPlatform.value?.fs_slug||'']||'#4466aa')

const menuItems = computed(()=>[
  {label:`View: ${gameView.value}`,action:()=>{gameView.value=gameView.value==='list'?'carousel':'list';localStorage.setItem('gd3_couch_view',gameView.value)}},
  {label:`Launch: ${launchMode.value}`,action:()=>{const m=['tab','window','fullscreen'];launchMode.value=m[(m.indexOf(launchMode.value)+1)%3];localStorage.setItem('gd3_couch_launch',launchMode.value)}},
  {label:`Bezel: ${bezelOn.value?'ON':'OFF'}`,action:()=>{bezelOn.value=!bezelOn.value;localStorage.setItem('gd3_couch_bezel',bezelOn.value?'on':'off')}},
  {label:'Resume',action:()=>{menuOpen.value=false}},
  {label:'Exit',action:()=>doExit(),danger:true},
])

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
  try{const{data}=await client.get(`/roms/${rom.id}`);const d:Detail={description:data.summary??null,screenshots:data.screenshots??null,developer:data.developer??null,genres:data.genres??null,ss_score:data.ss_score??null,wheel_path:data.wheel_path??null};cache.set(rom.id,d);if(selectedRom.value?.id===rom.id)detail.value=d}catch{}
}

function goSys(dir:number){const n=sysIdx.value+dir;if(n>=0&&n<platforms.value.length){sysIdx.value=n;loadDetail(n)}}
function selectPlatform(){state.value=gameView.value==='list'?'games-list':'games-carousel';fetchRoms()}
function backToSystems(){state.value='systems';roms.value=[];detail.value=null}
function doExit(){router.push('/')}
function launchGame(){
  const rom=selectedRom.value,plat=currentPlatform.value;if(!rom||!plat)return
  const core=getEjsCore(plat.fs_slug);if(!core)return
  const p:Record<string,string>={rom_id:String(rom.id),rom_name:rom.title,ejs_core:core,platform:plat.fs_slug}
  if(bezelOn.value)p.bezel='1'
  const url='/player.html?'+new URLSearchParams(p).toString()
  if(launchMode.value==='fullscreen')window.location.href=url+'&returnTo=/couch'
  else if(launchMode.value==='window')window.open(url,'gd3-player','width=1280,height=720,menubar=no,toolbar=no')
  else window.open(url,'_blank')
  couchNavPaused.value=true;window.addEventListener('focus',()=>{couchNavPaused.value=false},{once:true})
}

watch(sysIdx,(i)=>loadDetail(i))
watch(romIdx,()=>{detail.value=null;shotIdx.value=-1;if(dt)clearTimeout(dt);const r=selectedRom.value;if(r)dt=setTimeout(()=>loadRom(r),300);nextTick(()=>{(gameListRef.value?.querySelector('.cp-gl-row.selected') as HTMLElement)?.scrollIntoView({block:'nearest',behavior:'smooth'})})})
watch(gameView,(v)=>{if(state.value.startsWith('games-'))state.value=v==='list'?'games-list':'games-carousel'})

useCouchNav({
  up:()=>{if(menuOpen.value){menuIdx.value=Math.max(0,menuIdx.value-1);return}if(exitOpen.value){exitIdx.value=0;return}if(state.value==='systems')goSys(-1);if(state.value==='games-list'&&romIdx.value>0)romIdx.value--},
  down:()=>{if(menuOpen.value){menuIdx.value=Math.min(menuItems.value.length-1,menuIdx.value+1);return}if(exitOpen.value){exitIdx.value=1;return}if(state.value==='systems')goSys(1);if(state.value==='games-list'&&romIdx.value<roms.value.length-1)romIdx.value++},
  left:()=>{if(shotIdx.value>0){shotIdx.value--;return}if(state.value==='games-carousel'&&romIdx.value>0)romIdx.value--},
  right:()=>{if(shotIdx.value>=0&&detail.value?.screenshots&&shotIdx.value<detail.value.screenshots.length-1){shotIdx.value++;return}if(state.value==='games-carousel'&&romIdx.value<roms.value.length-1)romIdx.value++},
  confirm:()=>{if(menuOpen.value){menuItems.value[menuIdx.value]?.action();return}if(exitOpen.value){exitIdx.value===1?doExit():(exitOpen.value=false);return}if(state.value==='systems')selectPlatform();else launchGame()},
  back:()=>{if(shotIdx.value>=0){shotIdx.value=-1;return}if(menuOpen.value){menuOpen.value=false;return}if(exitOpen.value){exitOpen.value=false;return}if(state.value.startsWith('games-'))backToSystems();else exitOpen.value=true},
  menu:()=>{if(!exitOpen.value){menuOpen.value=!menuOpen.value;menuIdx.value=0}},
  x:()=>{if(detail.value?.screenshots?.length&&state.value.startsWith('games-'))shotIdx.value=0},
})

onMounted(()=>{document.documentElement.requestFullscreen?.().catch(()=>{});fetchPlatforms()})
</script>

<style scoped>
.cp{position:fixed;inset:0;z-index:9999;overflow:hidden;user-select:none;font-family:'Rajdhani',sans-serif;color:#fff}
.cp-bg{position:absolute;inset:0;z-index:0;background:var(--bg,#1e1e2e)}
.cp-fade-enter-active,.cp-fade-leave-active{transition:opacity .2s}.cp-fade-enter-from,.cp-fade-leave-to{opacity:0}
.cp-slide-enter-active,.cp-slide-leave-active{transition:opacity .35s}.cp-slide-enter-from,.cp-slide-leave-to{opacity:0}

/* ═══ SYSTEM VIEW ════════════════════════════════════════════════════ */
/* Right color block: pos 35.9% left, 4.5% top, 61.5% wide, 91% tall */
.cp-sys-block{position:absolute;left:35.9%;top:4.5%;width:61.5%;height:91%;z-index:2}
/* Platform image centered in color block */
.cp-sys-img-wrap{position:absolute;left:36.7%;top:4.5%;width:60%;height:91%;z-index:5;display:flex;align-items:center;justify-content:center;overflow:hidden}
.cp-sys-img{max-width:100%;max-height:100%;object-fit:contain}

/* Year: 2.6%, 15% */
.cp-sys-year{position:absolute;left:2.6%;top:15%;z-index:10;font-size:clamp(14px,3vh,28px);font-weight:300;letter-spacing:.03em}
/* Name: 2.6%, 22.5% */
.cp-sys-name{position:absolute;left:2.6%;top:22.5%;width:30.7%;z-index:10;font-family:'Orbitron',sans-serif;font-size:clamp(22px,5vh,52px);font-weight:900;line-height:1.1}
/* Desc: 2.6%, 44% */
.cp-sys-desc{position:absolute;left:2.6%;top:44%;width:30.7%;height:22%;z-index:10;font-size:clamp(11px,1.6vh,15px);color:rgba(255,255,255,.55);line-height:1.5;overflow-y:auto;scrollbar-width:none}
.cp-sys-desc::-webkit-scrollbar{display:none}

/* Bottom: 3 blocks at 72.2% y, each ~10.4vw x 18.6vh */
.cp-sys-bottom{position:absolute;left:2.55%;top:72.2%;display:flex;z-index:3;gap:0}
.cp-sys-bottom-block{width:10.4vw;height:18.6vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}
.cp-sys-bottom-block--dark{filter:brightness(.8)}
.cp-sys-bottom-block--light{filter:brightness(1.2)}
.cp-sys-bottom-icon{width:50%;height:auto;max-height:60%;object-fit:contain;filter:brightness(0) invert(1)}
.cp-sys-bottom-num{font-family:'Orbitron',sans-serif;font-size:clamp(18px,3vh,32px);font-weight:700}
.cp-sys-bottom-label{font-size:clamp(9px,1.1vh,12px);font-weight:700;text-transform:uppercase;letter-spacing:.12em}

/* Nav arrows: bottom right, white boxes */
.cp-sys-arrows{position:absolute;right:2.5%;bottom:7%;z-index:10;display:flex;gap:6px}
.cp-sys-arrow{width:40px;height:40px;background:rgba(255,255,255,.9);color:#333;border:none;border-radius:4px;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .15s}
.cp-sys-arrow:hover{background:#fff}

/* ═══ GAME LIST — list-video style ═══════════════════════════════════ */
/* Color panel: 2.6%, 4.6%, 37% wide (list only, not full 56%) */
.cp-gl-panel{position:absolute;left:2.6%;top:4.6%;width:37%;height:90.8%;z-index:1}

/* System logo: icon + SVG name, top of list */
.cp-gl-syslogo-wrap{position:absolute;left:5.2%;top:7%;z-index:10;display:flex;align-items:center;gap:10px}
.cp-gl-syslogo-icon{height:clamp(28px,5vh,48px);width:auto;filter:brightness(0) invert(1)}
.cp-gl-syslogo-name{height:clamp(20px,3.5vh,36px);width:auto;max-width:20vw;filter:brightness(0) invert(1)}

/* Text list: just names, rounded pill for selected */
.cp-gl-list{position:absolute;left:5.2%;top:18%;width:30%;height:74%;z-index:10;overflow-y:auto;scrollbar-width:none}
.cp-gl-list::-webkit-scrollbar{display:none}
.cp-gl-row{padding:7px 16px;font-size:clamp(14px,2.2vh,20px);font-weight:700;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-radius:99px;margin-bottom:1px;transition:background .1s}
.cp-gl-row:not(.selected){color:rgba(255,255,255,.45)}
.cp-gl-row.selected{background:rgba(255,255,255,.95);color:var(--sys-color,#4466aa)}

/* Big image on right (like list-video in Pop: screenshot centered in color block area) */
.cp-gl-bigimage{position:absolute;left:42%;top:4.5%;width:56%;height:91%;z-index:5;display:flex;align-items:center;justify-content:center;overflow:hidden}
.cp-gl-bigimage-img{max-width:95%;max-height:95%;object-fit:contain}

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
.cp-help{position:absolute;bottom:0;left:0;right:0;z-index:50;padding:10px 0;display:flex;gap:24px;justify-content:center;font-size:12px;color:rgba(255,255,255,.25);letter-spacing:.02em}

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
</style>
