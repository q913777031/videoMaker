// 入口：加载时间轴 → 构建全部镜头 → 暴露 window.AC.seek(t)，供逐帧渲染器调用。
import {
  THREE, W, H, PAL, TL, loadTimeline, initRenderer, paintPaper, inkWipe, clamp01, easeOut, easeIn, prog, lerp,
} from './engine.js';
import { SHOT_FACTORIES } from './shots/index.js';

const params = new URLSearchParams(location.search);

// ---------------------------------------------------------------- DOM 界面层
const uiRoot = document.getElementById('ui');
function el(tag, css, parent = uiRoot, html = '') {
  const e = document.createElement(tag);
  Object.assign(e.style, { position: 'absolute', ...css });
  e.innerHTML = html;
  parent.appendChild(e);
  return e;
}

/** 镜头私有 UI：每个镜头一个容器，只在镜头激活时显示。 */
export class ShotUI {
  constructor() { this.root = el('div', { inset: '0', display: 'none' }); this.items = {}; }
  add(id, html, css) { this.items[id] = el('div', css, this.root, html); return this.items[id]; }
  /** 书法大字：每个字单独一个 span，brush(id, k) 逐字落笔（k∈[0,1]）。 */
  brushText(id, text, css) {
    const e = this.add(id, [...text].map(ch => `<span style="display:inline-block;opacity:0">${ch}</span>`).join(''),
      { font: '200px MaShanZheng', color: PAL.ink, whiteSpace: 'nowrap', left: '540px', top: '700px',
        transform: 'translate(-50%, -50%)', ...css });
    e._chars = [...e.querySelectorAll('span')];
    return e;
  }
  brush(id, k, stagger = 0.75) {
    const e = this.items[id];
    const n = e._chars.length;
    e._chars.forEach((c, i) => {
      const q = clamp01((k * (n * (1 - stagger) + stagger * n) - i * stagger) / 1.0);
      const a = clamp01(q * 1.6);
      c.style.opacity = String(a);
      c.style.transform = `scale(${1.25 - 0.25 * easeOut(q)})`;
      c.style.filter = q < 1 ? `blur(${(1 - q) * 3}px)` : 'none';
    });
  }
  /** 朱砂印章（白文）：stamp(id, dt) 以 dt=0 为落章拍点，0.12 秒内从 1.8 倍砸到原大并轻微回弹。 */
  sealStamp(id, text, css) {
    const n = [...text].length;
    const cols = n <= 2 ? 1 : 2;
    const html = `<div style="width:${cols * 96 + 40}px;height:${Math.ceil(n / cols) * 96 + 40}px;background:${PAL.cinnabar};
      border-radius:14px;display:flex;flex-direction:column;flex-wrap:wrap;align-content:center;justify-content:center;
      box-shadow:inset 0 0 0 7px ${PAL.cinnabar}, inset 0 0 0 11px #F3E3D3;writing-mode:vertical-rl;
      font:900 88px NotoSerifSC;color:#F7EDE3;line-height:96px;letter-spacing:4px;filter:url(#rough)">${text}</div>`;
    return this.add(id, html, { left: '540px', top: '900px', opacity: 0, ...css });
  }
  stamp(id, dt, { x = null, y = null, r = -6 } = {}) {
    if (dt < 0) { this.set(id, { o: 0, x, y }); return; }
    const k = clamp01(dt / 0.12);
    const s = dt < 0.12 ? lerp(1.8, 1, easeIn(k)) : 1 + 0.06 * Math.exp(-(dt - 0.12) * 12) * Math.cos((dt - 0.12) * 40);
    this.set(id, { o: clamp01(dt / 0.05), x, y, s, r });
  }
  set(id, { o = null, x = null, y = null, s = 1, r = 0, html = null } = {}) {
    const e = this.items[id];
    if (o !== null) e.style.opacity = String(clamp01(o));
    if (html !== null && e._html !== html) { e.innerHTML = html; e._html = html; }
    const tx = x === null ? '' : `translate(${x}px, ${y}px) `;
    e.style.transform = `${tx}translate(-50%, -50%) scale(${s}) rotate(${r}deg)`;
  }
}

const HALO = '0 0 10px rgba(246,238,222,1), 0 0 4px rgba(246,238,222,1)';
const header = el('div', { left: '64px', top: '170px', font: '500 30px NotoSansSC', color: PAL.ink2, letterSpacing: '2px', textShadow: HALO });
const headTitle = el('div', { left: '64px', top: '214px', font: '64px MaShanZheng', color: PAL.ink, whiteSpace: 'nowrap', textShadow: HALO });
const tagEl = el('div', { right: '64px', top: '226px', font: '700 28px NotoSansSC', padding: '8px 22px', borderRadius: '30px',
  border: '3px solid', background: 'rgba(248,242,231,0.85)' });
const capEl = el('div', { left: '0', width: `${W}px`, top: '1330px', textAlign: 'center', font: '700 62px NotoSerifSC',
  color: PAL.ink, lineHeight: '96px', textShadow: '0 0 14px rgba(246,238,222,0.95), 0 0 4px rgba(246,238,222,1)' });
const noteEl = el('div', { left: '0', width: `${W}px`, top: '1262px', textAlign: 'center', font: '500 28px NotoSansSC',
  color: PAL.ink2, textShadow: '0 0 8px rgba(246,238,222,1)' });

function richHTML(s) {
  return s.split('|').map(line => line.replace(/【(.*?)】/g,
    `<span style="color:${PAL.cinnabar};background:linear-gradient(transparent 62%, rgba(194,58,43,0.18) 62%)">$1</span>`))
    .join('<br>');
}

const TAG_COLORS = { '原理': PAL.azure, '实验': PAL.jade, '标准': PAL.ochre, '误区': PAL.cinnabar, '建议': PAL.jade,
  '情境': PAL.ink2, '结论': PAL.cinnabar, '出处': PAL.ink2 };

function drawUI(t, si) {
  const sh = TL.shots[si];
  const a = clamp01((t - 0.3) / 0.6) * (1 - prog(t, TL.end - 1.2, 1.0));
  header.style.opacity = a;
  headTitle.style.opacity = a;
  header.textContent = TL.series || '';
  headTitle.textContent = TL.title_short || '';
  if (sh.tag) {
    const c = Object.entries(TAG_COLORS).find(([k]) => sh.tag.startsWith(k));
    tagEl.style.color = c ? c[1] : PAL.ink2;
    tagEl.style.borderColor = c ? c[1] : PAL.ink2;
    tagEl.textContent = sh.tag;
    tagEl.style.opacity = a * easeOut(prog(t, sh.t0, 0.4));
  } else tagEl.style.opacity = 0;
  const cap = TL.captions.find(c => t >= c.t0 - 0.01 && t < c.t1);
  if (cap) {
    const k = easeOut(prog(t, cap.t0, 0.38)), out = 1 - easeIn(prog(t, cap.t1 - 0.28, 0.28));
    if (capEl._text !== cap.text) { capEl.innerHTML = richHTML(cap.text); capEl._text = cap.text; }
    capEl.style.opacity = String(k * out);
    capEl.style.transform = `translateY(${(1 - k) * 28 + (1 - out) * 14}px)`;
    if (cap.note) {
      if (noteEl._text !== cap.note) { noteEl.textContent = cap.note; noteEl._text = cap.note; }
      noteEl.style.opacity = String(k * out * easeOut(prog(t, cap.t0 + 0.4, 0.4)));
    } else noteEl.style.opacity = 0;
  } else { capEl.style.opacity = 0; noteEl.style.opacity = 0; }
}

// ---------------------------------------------------------------- 水墨特效层
const fx = document.getElementById('fx').getContext('2d');
function drawFX(t, si, shot) {
  fx.clearRect(0, 0, W, H);
  for (let i = 1; i < TL.shots.length; i++) {          // 镜头边界的泼墨转场：拍点上完全遮住
    const s = TL.shots[i];
    if (s.transition !== 'ink') continue;
    const k = (t - (s.t0 - 0.3)) / 0.3;
    if (k > 0 && k < 2) inkWipe(fx, k, i % 2 ? 1 : -1, PAL.ink, 7 + i);
  }
  if (shot.fx) shot.fx(fx, t - TL.shots[si].t0, t);
  const fin = 1 - clamp01(t / 0.45), fout = clamp01((t - (TL.end - 1.1)) / 1.0);
  const veil = Math.max(fin, fout);
  if (veil > 0) { fx.fillStyle = `rgba(239,230,211,${veil})`; fx.fillRect(0, 0, W, H); }
}

// ---------------------------------------------------------------- 启动
let SHOTS = [];
let active = -1;
let renderer = null;

async function boot() {
  const data = await (await fetch('./timeline.json')).json();
  loadTimeline(data);
  paintPaper(document.getElementById('paper'));
  renderer = initRenderer(document.getElementById('gl'));
  await document.fonts.load('64px MaShanZheng');
  await document.fonts.load('700 62px NotoSerifSC');
  await document.fonts.load('900 62px NotoSerifSC');
  await document.fonts.load('500 30px NotoSansSC');
  await document.fonts.load('700 30px NotoSansSC');
  const only = params.get('only');                     // 只构建指定镜头（检查静帧时加快启动）
  SHOTS = TL.shots.map(s => {
    const f = only && only.split(',').indexOf(s.name) < 0 ? stubShot : SHOT_FACTORIES[s.name];
    if (!f) throw new Error('no shot factory for ' + s.name);
    const ui = new ShotUI();
    const shot = f({ ui, info: s });
    shot.ui = ui;
    return shot;
  });
  // 预编译着色器，避免首帧卡顿影响确定性
  for (const sh of SHOTS) renderer.compile(sh.scene, sh.camera);
  window.AC.ready = true;
}

function stubShot() {
  return { scene: new THREE.Scene(), camera: new THREE.PerspectiveCamera(35, W / H, 0.1, 10), update() {} };
}

function shotIndex(t) {
  for (let i = TL.shots.length - 1; i >= 0; i--) if (t >= TL.shots[i].t0) return i;
  return 0;
}

window.AC = {
  ready: false,
  seek(t) {
    const i = shotIndex(t);
    if (i !== active) {
      if (active >= 0) SHOTS[active].ui.root.style.display = 'none';
      SHOTS[i].ui.root.style.display = 'block';
      active = i;
    }
    const sh = SHOTS[i];
    const lt = t - TL.shots[i].t0;
    sh.update(lt, t);
    renderer.render(sh.scene, sh.camera);
    drawUI(t, i);
    drawFX(t, i, sh);
    return i;
  },
  info() { return { shots: TL.shots.length, end: TL.end }; },
};

boot().catch(e => { window.AC.error = String(e && e.stack || e); console.error(e); });
