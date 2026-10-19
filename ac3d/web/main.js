// 入口：加载时间轴 → 构建整片唯一的客厅场景 → 暴露 window.AC.seek(t)，供逐帧渲染器调用。
// 画面层次：#bg 浅色渐变底 → #gl three.js 场景 → #fx 淡入淡出 → #ui DOM 字幕与标签。
import { W, H, TL, loadTimeline, initRenderer, clamp01, easeOut, easeIn, prog } from './engine.js';
import { MOD } from './room.js';
import { createFilm } from './film.js';

const uiRoot = document.getElementById('ui');
function el(css, html = '') {
  const e = document.createElement('div');
  Object.assign(e.style, { position: 'absolute', ...css });
  e.innerHTML = html;
  uiRoot.appendChild(e);
  return e;
}

const HALO = '0 0 12px rgba(255,255,255,1), 0 0 4px rgba(255,255,255,1)';
const header = el({ left: '64px', top: '168px', font: '500 30px NotoSansSC', color: MOD.ink2, letterSpacing: '2px', textShadow: HALO });
const headTitle = el({ left: '64px', top: '210px', font: '900 64px NotoSansSC', color: MOD.ink, whiteSpace: 'nowrap', textShadow: HALO });
const tagEl = el({ right: '64px', top: '228px', font: '700 30px NotoSansSC', padding: '8px 24px', borderRadius: '30px', color: '#fff' });
const capEl = el({ left: '540px', top: '1330px', textAlign: 'center', font: '700 64px NotoSansSC', whiteSpace: 'nowrap',
  color: MOD.ink, lineHeight: '92px', padding: '14px 46px', borderRadius: '30px', background: 'rgba(255,255,255,0.86)',
  boxShadow: '0 8px 26px rgba(20,30,40,0.12)' });
const noteEl = el({ left: '90px', width: `${W - 180}px`, top: '1576px', textAlign: 'center', font: '500 30px NotoSansSC',
  color: MOD.ink2, lineHeight: '44px', padding: '10px 28px', boxSizing: 'border-box', borderRadius: '20px',
  background: 'rgba(255,255,255,0.8)' });

function richHTML(s) {
  return s.split('|').map(line => line.replace(/【(.*?)】/g, `<span style="color:#E2701D">$1</span>`)).join('<br>');
}

const TAG_COLORS = { '情境': '#5B6875', '问题': '#5B6875', '原理': MOD.cool, '实验': MOD.ok, '误区': MOD.hot, '提示': MOD.heat,
  '结论': MOD.hot, '出处': '#5B6875' };

function drawUI(t, si) {
  const sh = TL.shots[si];
  const a = clamp01((t - 0.3) / 0.6) * (1 - prog(t, TL.end - 1.2, 1.0));
  header.style.opacity = a;
  headTitle.style.opacity = a;
  header.textContent = TL.series || '';
  headTitle.textContent = TL.title_short || '';
  // 角标：镜头切换时旧角标淡出、新角标淡入（不硬切）
  const k = prog(t, sh.t0 - 0.2, 0.45);
  const prev = si > 0 ? TL.shots[si - 1].tag : '';
  const tag = k < 0.5 && prev ? prev : sh.tag;
  tagEl.textContent = tag;
  tagEl.style.background = TAG_COLORS[tag] || MOD.ink2;
  tagEl.style.opacity = String(a * (prev && prev !== sh.tag ? Math.abs(1 - 2 * k) : 1));
  const cap = TL.captions.find(c => t >= c.t0 - 0.01 && t < c.t1);
  if (cap) {
    const ki = easeOut(prog(t, cap.t0, 0.38)), out = 1 - easeIn(prog(t, cap.t1 - 0.28, 0.28));
    if (capEl._text !== cap.text) { capEl.innerHTML = richHTML(cap.text); capEl._text = cap.text; }
    capEl.style.opacity = String(ki * out);
    capEl.style.transform = `translateX(-50%) translateY(${(1 - ki) * 24 + (1 - out) * 12}px)`;
    if (cap.note) {
      if (noteEl._text !== cap.note) { noteEl.textContent = cap.note; noteEl._text = cap.note; }
      noteEl.style.opacity = String(ki * out * easeOut(prog(t, cap.t0 + 0.4, 0.4)));
    } else noteEl.style.opacity = 0;
  } else { capEl.style.opacity = 0; noteEl.style.opacity = 0; }
}

const fx = document.getElementById('fx').getContext('2d');
function drawFX(t) {
  fx.clearRect(0, 0, W, H);
  const veil = Math.max(1 - clamp01(t / 0.5), clamp01((t - (TL.end - 1.1)) / 1.0));
  if (veil > 0) { fx.fillStyle = `rgba(244,247,249,${veil})`; fx.fillRect(0, 0, W, H); }
}

function paintBackground(canvas) {
  const g = canvas.getContext('2d');
  const lin = g.createLinearGradient(0, 0, 0, H);
  lin.addColorStop(0, '#F5F8FA');
  lin.addColorStop(0.55, MOD.bg);
  lin.addColorStop(1, MOD.bg2);
  g.fillStyle = lin; g.fillRect(0, 0, W, H);
  const rad = g.createRadialGradient(W / 2, H * 0.48, 80, W / 2, H * 0.48, H * 0.6);
  rad.addColorStop(0, 'rgba(255,255,255,0.7)');
  rad.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = rad; g.fillRect(0, 0, W, H);
}

let film = null, renderer = null;

async function boot() {
  const data = await (await fetch('./timeline.json')).json();
  loadTimeline(data);
  paintBackground(document.getElementById('bg'));
  renderer = initRenderer(document.getElementById('gl'));
  for (const f of ['500 30px NotoSansSC', '700 30px NotoSansSC', '900 30px NotoSansSC']) await document.fonts.load(f);
  film = createFilm();
  renderer.compile(film.scene, film.camera);
  window.AC.ready = true;
}

function shotIndex(t) {
  for (let i = TL.shots.length - 1; i >= 0; i--) if (t >= TL.shots[i].t0) return i;
  return 0;
}

window.AC = {
  ready: false,
  seek(t) {
    const i = shotIndex(t);
    film.update(t - TL.shots[i].t0, t);
    renderer.render(film.scene, film.camera);
    drawUI(t, i);
    drawFX(t);
    return i;
  },
  info() { return { shots: TL.shots.length, end: TL.end }; },
};

boot().catch(e => { window.AC.error = String(e && e.stack || e); console.error(e); });
