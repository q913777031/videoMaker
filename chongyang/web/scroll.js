// 水墨长卷通用框架：整片是一幅横向长卷，镜头沿卷连续平移（没有硬切）；远山两层视差、云雾、近景小景随镜头经过。
// 互动答题卡在屏幕空间：展开 → 3 秒倒计时（3、2、1 各落在实测拍点上）→ 下一镜第 0 拍揭晓（朱砂“对”印）→ 卷起。
// 各短片只需提供：每个镜头的小景绘制函数 scenes[name](g, ox, t)、精灵构建函数、震屏时刻、远景装饰与前景层（可选）。
import {
  W, H, INK, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, rng, canvas, paintPaper, mountains, mist,
  stamp, warmMountains, stroke,
} from './ink.js';

export const TL = {};
export const cue = n => { if (!(n in TL.cues)) throw new Error('unknown cue ' + n); return TL.cues[n]; };
const SPAN = 1500;                                       // 相邻镜头在长卷上的间距（像素）

// ---------------------------------------------------------------- DOM：页眉、角标、字幕
const uiRoot = document.getElementById('ui');
function el(css, html = '') {
  const e = document.createElement('div');
  Object.assign(e.style, { position: 'absolute', ...css });
  e.innerHTML = html;
  uiRoot.appendChild(e);
  return e;
}
const HALO = '0 0 10px rgba(246,238,222,1), 0 0 4px rgba(246,238,222,1)';
const header = el({ left: '64px', top: '170px', font: '500 30px NotoSansSC', color: INK.ink2, letterSpacing: '2px', textShadow: HALO });
const headTitle = el({ left: '64px', top: '212px', font: '66px MaShanZheng', color: INK.ink, whiteSpace: 'nowrap', textShadow: HALO });
const tagEl = el({ right: '64px', top: '228px', font: '700 28px NotoSansSC', padding: '8px 22px', borderRadius: '30px',
  border: `3px solid ${INK.red}`, color: INK.red, background: 'rgba(248,242,231,0.85)' });
const capEl = el({ left: '0', width: `${W}px`, top: '1330px', textAlign: 'center', font: '700 62px NotoSerifSC',
  color: INK.ink, lineHeight: '96px', textShadow: '0 0 14px rgba(246,238,222,0.95), 0 0 4px rgba(246,238,222,1)' });
const noteEl = el({ left: '70px', width: `${W - 140}px`, top: '1540px', textAlign: 'center', font: '500 28px NotoSansSC',
  color: INK.ink2, lineHeight: '42px', textShadow: '0 0 8px rgba(246,238,222,1), 0 0 3px rgba(246,238,222,1)' });
/** 主题：{ headFont, titleFont, capFont, ink, ink2, accent, halo, tagBg } 覆盖页眉、角标、字幕的样式。 */
let ACCENT = INK.red;
function applyTheme(th) {
  const halo = th.halo || 'rgba(246,238,222,1)';
  const sh = `0 0 10px ${halo}, 0 0 4px ${halo}`;
  if (th.headFont) header.style.font = th.headFont;
  if (th.titleFont) headTitle.style.font = th.titleFont;
  if (th.capFont) capEl.style.font = th.capFont;
  if (th.ink) { headTitle.style.color = th.ink; capEl.style.color = th.ink; }
  if (th.ink2) { header.style.color = th.ink2; noteEl.style.color = th.ink2; }
  if (th.accent) { ACCENT = th.accent; tagEl.style.color = th.accent; tagEl.style.borderColor = th.accent; }
  if (th.tagBg) tagEl.style.background = th.tagBg;
  if (th.tagFont) tagEl.style.font = th.tagFont;
  if (th.tagRadius) tagEl.style.borderRadius = th.tagRadius;
  if (th.letterSpacing) headTitle.style.letterSpacing = th.letterSpacing;
  header.style.textShadow = sh; headTitle.style.textShadow = sh;
  capEl.style.textShadow = `0 0 14px ${halo}, 0 0 4px ${halo}`; noteEl.style.textShadow = sh;
}
const richHTML = s => s.split('|').map(line => line.replace(/【(.*?)】/g, `<span style="color:${ACCENT}">$1</span>`)).join('<br>');

function drawUI(t, si) {
  const sh = TL.shots[si];
  const a = clamp01((t - 0.3) / 0.6) * (1 - prog(t, TL.end - 1.2, 1.0));
  header.style.opacity = a; headTitle.style.opacity = a;
  header.textContent = TL.series; headTitle.textContent = TL.title_short;
  const k = prog(t, sh.t0 - 0.2, 0.45);
  const prev = si > 0 ? TL.shots[si - 1].tag : '';
  tagEl.textContent = k < 0.5 && prev ? prev : sh.tag;
  tagEl.style.opacity = String(a * (prev && prev !== sh.tag ? Math.abs(1 - 2 * k) : 1));
  const cap = TL.captions.find(c => t >= c.t0 - 0.01 && t < c.t1);
  if (cap) {
    const ki = easeOut(prog(t, cap.t0, 0.38)), out = 1 - easeIn(prog(t, cap.t1 - 0.28, 0.28));
    if (capEl._t !== cap.text) { capEl.innerHTML = richHTML(cap.text); capEl._t = cap.text; }
    capEl.style.opacity = String(ki * out);
    capEl.style.transform = `translateY(${(1 - ki) * 26 + (1 - out) * 12}px)`;
    if (cap.note) {
      if (noteEl._t !== cap.note) { noteEl.textContent = cap.note; noteEl._t = cap.note; }
      noteEl.style.opacity = String(ki * out * easeOut(prog(t, cap.t0 + 0.4, 0.4)));
    } else noteEl.style.opacity = 0;
  } else { capEl.style.opacity = 0; noteEl.style.opacity = 0; }
}

// ---------------------------------------------------------------- 长卷镜头
let KEYS = [];
function camX(t) {
  let i = 0;
  while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++;
  const [ta, xa] = KEYS[i], [tb, xb] = KEYS[i + 1];
  return lerp(xa, xb, easeInOut(prog(t, ta, tb - ta)));
}
let SHAKES = [];
function shakeAt(t) {
  let dx = 0, dy = 0;
  for (const [n, amp] of SHAKES) {
    const d = t - cue(n);
    if (d < 0 || d > 0.4) continue;
    const k = Math.exp(-d * 10) * amp;
    dx += Math.sin(d * 61) * k; dy += Math.cos(d * 47) * k;
  }
  return [dx, dy];
}

// ---------------------------------------------------------------- 小景绘制辅助
export const P = (t, n, d = 0.5, ease = easeOut) => ease(prog(t, cue(n), d));
export function label(g, text, x, y, a = 1, size = 42) {
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; g.font = `700 ${size}px NotoSerifSC`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = 8; g.strokeStyle = 'rgba(244,238,226,0.9)'; g.strokeText(text, x, y);
  g.fillStyle = INK.ink; g.fillText(text, x, y); g.restore();
}
export function draw(g, sp, x, yBase, s = 1, a = 1) {
  if (a <= 0) return;
  g.globalAlpha = a; g.drawImage(sp, x - sp.width * s / 2, yBase - sp.height * s, sp.width * s, sp.height * s); g.globalAlpha = 1;
}

// ---------------------------------------------------------------- 答题卡
let CARD = null;
function cardSprite() {
  const c = canvas(940, 800), g = c.getContext('2d');
  g.fillStyle = 'rgba(60,40,20,0.18)'; g.filter = 'blur(14px)'; g.fillRect(30, 40, 880, 740); g.filter = 'none';
  g.fillStyle = '#F7EFDF'; g.fillRect(20, 20, 900, 760);
  const r = rng(3);
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(120,96,60,${0.03 + r() * 0.04})`; g.fillRect(20 + r() * 900, 20 + r() * 760, 1 + r() * 14, 1); }
  const box = (x0, y0, x1, y1, w, seed) => {
    stroke(g, [[x0, y0], [x1, y0]], w, { seed, dry: 2, taper: [0.03, 0.06] });
    stroke(g, [[x1, y0], [x1, y1]], w, { seed: seed + 1, dry: 2, taper: [0.03, 0.06] });
    stroke(g, [[x1, y1], [x0, y1]], w, { seed: seed + 2, dry: 2, taper: [0.03, 0.06] });
    stroke(g, [[x0, y1], [x0, y0]], w, { seed: seed + 3, dry: 2, taper: [0.03, 0.06] });
  };
  box(40, 40, 900, 760, 9, 10);
  box(58, 58, 882, 742, 3, 20);
  return c;
}
const NUM = ['一', '二', '三', '四'];
function drawCard(g, t) {
  (TL.quiz || []).forEach((q, qi) => {
    const tc = cue(q.shot + '.card'), c3 = cue(q.shot + '.c3'), tr = cue(q.answer_shot + '.reveal');
    if (t < tc - 0.25 || t > tr + 1.7) return;
    const ku = easeOut(prog(t, tc - 0.25, 0.4)), ke = easeIn(prog(t, tr + 1.05, 0.55));
    const cx = 540, cy = 830;
    g.save();
    g.translate(cx, 430 + ke * 400);
    g.scale(1 - ke * 0.3, ku * (1 - ke));
    g.globalAlpha = 1 - ke;
    g.translate(-cx, -430);
    g.drawImage(CARD, cx - 470, 430);
    stamp(g, `第${NUM[qi]}题`, cx - 330, 540, Math.max(0.2, t - tc), { size: 96, rot: -0.05 });
    const lines = q.q.split('|');
    g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = INK.ink;
    g.font = '700 60px NotoSerifSC';
    lines.forEach((ln, i) => { g.globalAlpha = (1 - ke) * clamp01((t - tc - i * 0.15) / 0.3); g.fillText(ln, cx + 40, 560 + i * 90); });
    q.opts.forEach((o, i) => {
      const bx = cx + (i ? 215 : -215), by = 860;
      const kp = easeOutBack(prog(t, tc + 0.3 + i * 0.15, 0.35), 2);
      if (kp <= 0) return;
      const correct = i === q.answer, after = t >= tr;
      const dim = after && !correct ? 0.35 : 1;
      g.save(); g.globalAlpha = (1 - ke) * dim * clamp01(kp * 2); g.translate(bx, by); g.scale(kp, kp);
      g.fillStyle = after && correct ? 'rgba(184,55,43,0.1)' : 'rgba(255,255,255,0.55)';
      g.strokeStyle = after && correct ? INK.red : INK.ink; g.lineWidth = after && correct ? 7 : 4;
      g.beginPath(); g.roundRect(-190, -78, 380, 156, 22); g.fill(); g.stroke();
      g.fillStyle = INK.red; g.beginPath(); g.arc(-128, 0, 38, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#F7EDE3'; g.font = '700 46px NotoSerifSC'; g.fillText(i ? 'B' : 'A', -128, 2);
      g.fillStyle = INK.ink; g.font = `700 ${o.length > 3 ? 46 : 54}px NotoSerifSC`; g.fillText(o, 36, 2);
      g.restore();
      if (after && correct) stamp(g, '对', bx + 150, by - 70, t - tr, { size: 110, rot: 0.12 });
    });
    if (t >= c3 - 0.1 && t < tr + 0.05) {                     // 倒计时圈：3 → 2 → 1，到揭晓那一拍收尽
      const rem = 1 - clamp01((t - c3) / (tr - c3));
      g.globalAlpha = 1 - ke;
      g.strokeStyle = 'rgba(42,38,34,0.15)'; g.lineWidth = 14;
      g.beginPath(); g.arc(cx, 1070, 62, 0, Math.PI * 2); g.stroke();
      g.strokeStyle = INK.red; g.lineCap = 'round';
      g.beginPath(); g.arc(cx, 1070, 62, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * rem); g.stroke();
      const steps = [[c3, '3'], [cue(q.shot + '.c2'), '2'], [cue(q.shot + '.c1'), '1']];
      let cur = null;
      for (const s of steps) if (t >= s[0] - 0.02) cur = s;
      if (cur) {
        const d = t - cur[0], s = 1 + 0.35 * Math.exp(-d * 9);
        g.save(); g.translate(cx, 1072); g.scale(s, s);
        g.fillStyle = INK.ink; g.font = '110px MaShanZheng'; g.fillText(cur[1], 0, 4); g.restore();
      }
    }
    g.globalAlpha = (1 - ke) * clamp01((t - tc - 0.6) / 0.4);
    g.fillStyle = INK.ink2; g.font = '500 32px NotoSansSC';
    g.fillText(t < tr ? '想好了吗？在评论区打出 A 或 B' : `答案：${q.answer ? 'B' : 'A'} ${q.opts[q.answer]}`, cx, 1170);
    g.restore();
  });
}

// ---------------------------------------------------------------- 每帧
let ctx = null, PAPER = null, SCENES = {}, BACKDROP = null, OVERLAY = null, GROUND = null, PAPER_FN = null, VEIL = 'rgba(239,230,211,';
function frame(t, si) {
  const g = ctx;
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.drawImage(PAPER, 0, 0);
  const cx = camX(t);
  const [sx, sy] = shakeAt(t);
  g.setTransform(1, 0, 0, 1, sx, sy);
  if (BACKDROP) BACKDROP(g, cx, t);
  if (GROUND) GROUND(g, cx, t);
  else {
    mountains(g, 'far', cx);
    mist(g, 900, 260, t, cx, 0.3, 0.75, 3);
    mountains(g, 'mid', cx);
    mist(g, 1160, 300, t, cx, 0.55, 0.85, 7);
  }
  for (const s of TL.shots) {
    const ox = s.x - cx + W / 2;
    if (ox < -1200 || ox > W + 1200) continue;
    const f = SCENES[s.name];
    if (f) f(g, ox, t);
  }
  if (OVERLAY) OVERLAY(g, cx, t);
  if (!GROUND) mist(g, 1330, 260, t, cx, 1.0, 0.55, 11);
  const fade = g.createLinearGradient(0, 1250, 0, 1620);       // 字幕区淡去，让文字干净
  fade.addColorStop(0, VEIL + '0)'); fade.addColorStop(1, VEIL + '0.85)');
  g.fillStyle = fade; g.fillRect(-40, 1250, W + 80, 700);
  drawCard(g, t);
  g.setTransform(1, 0, 0, 1, 0, 0);
  const veil = Math.max(1 - clamp01(t / 0.5), clamp01((t - (TL.end - 1.1)) / 1.0));
  if (veil > 0) { g.fillStyle = `${VEIL}${veil})`; g.fillRect(0, 0, W, H); }
  drawUI(t, si);
}

async function boot(sprites, fontSample) {
  Object.assign(TL, await (await fetch('./timeline.json')).json());
  TL.shot = {};
  TL.shots.forEach((s, i) => { s.x = i * SPAN; TL.shot[s.name] = s; });
  KEYS = [[0, -160]];
  TL.shots.forEach((s, i) => { if (i) KEYS.push([s.t0 + 1.0, s.x - 40]); KEYS.push([s.t1 - 0.35, s.x + 40]); });
  KEYS.push([TL.end + 1, TL.shots[TL.shots.length - 1].x + 60]);
  for (const f of ['66px MaShanZheng', '700 60px NotoSerifSC', '900 60px NotoSerifSC', '500 30px NotoSansSC', '700 30px NotoSansSC']) await document.fonts.load(f, fontSample);
  const c = document.getElementById('c');
  ctx = c.getContext('2d');
  PAPER = canvas(W, H); (PAPER_FN || paintPaper)(PAPER.getContext('2d'));
  CARD = cardSprite();
  sprites();
  if (!GROUND) warmMountains(-1200, TL.shots[TL.shots.length - 1].x + 1200);
  window.AC.ready = true;
}

/** 启动长卷：scenes 为 {镜头名: (g, ox, t) => void}，ox 是该镜头在屏幕上的中心 x。
 *  可选：ground(g, cx, t) 替换默认的远山云雾；paper(g) 替换宣纸底；theme 改页眉字幕的字体配色；veil 为淡入淡出底色（'rgba(r,g,b,'）。 */
export function runScroll({ scenes, sprites, shakes = [], backdrop = null, overlay = null, fontSample = '一二三四',
  ground = null, paper = null, theme = null, veil = null }) {
  SCENES = scenes; SHAKES = shakes; BACKDROP = backdrop; OVERLAY = overlay; GROUND = ground; PAPER_FN = paper;
  if (veil) VEIL = veil;
  if (theme) applyTheme(theme);
  boot(sprites, fontSample).catch(e => { window.AC.error = String(e && e.stack || e); console.error(e); });
}

const shotIndex = t => { for (let i = TL.shots.length - 1; i >= 0; i--) if (t >= TL.shots[i].t0) return i; return 0; };
window.AC = {
  ready: false,
  seek(t) { const i = shotIndex(t); frame(t, i); return i; },
  info() { return { shots: TL.shots.length, end: TL.end }; },
};
