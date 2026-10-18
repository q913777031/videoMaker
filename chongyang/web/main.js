// 水墨长卷：整片是一幅横向长卷，镜头沿卷连续平移（没有硬切）；远山两层视差、云雾、近景小景随镜头经过。
// 互动答题卡在屏幕空间：展开 → 3 秒倒计时（3、2、1 各落在实测拍点上）→ 下一镜第 0 拍揭晓（朱砂“对”印）→ 卷起。
import {
  W, H, INK, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, win, rng, canvas, rgba, paintPaper, mountains, mist,
  brushText, stamp, warmMountains, splash, blot, reveal, stroke, pine, chrysanthemum, zhuyu, crane, figure, pavilion, palace, village, darkCloud,
  cakeLayer, cakePlate, winePot, climbMountain, geese, roundFan,
} from './ink.js';

const TL = {};
const cue = n => { if (!(n in TL.cues)) throw new Error('unknown cue ' + n); return TL.cues[n]; };
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
const richHTML = s => s.split('|').map(line => line.replace(/【(.*?)】/g, `<span style="color:${INK.red}">$1</span>`)).join('<br>');

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
function shakeAt(t) {
  let dx = 0, dy = 0;
  for (const [n, amp] of [['a1.reveal', 14], ['a1.nine2', 10], ['legend.cloud', 8], ['a4.final', 16]]) {
    const d = t - cue(n);
    if (d < 0 || d > 0.4) continue;
    const k = Math.exp(-d * 10) * amp;
    dx += Math.sin(d * 61) * k; dy += Math.cos(d * 47) * k;
  }
  return [dx, dy];
}

// ---------------------------------------------------------------- 小景
let SP = {};
function buildSprites() {
  const mtn = climbMountain();
  const cakeStack = canvas(420, 330);
  { const g = cakeStack.getContext('2d'); [380, 310, 240].forEach((w, i) => { const c = cakeLayer(w, i + 1); g.drawImage(c, 210 - c.width / 2, 330 - 120 - i * 70 + 20); }); }
  SP = {
    mtn, pav: pavilion(), pine: pine(3), pine2: pine(9), chry: chrysanthemum(5), zhuyu: zhuyu(7), zhuyuS: zhuyu(11, 0.7),
    craneFly: crane(true), craneStand: crane(false), palace: palace(), village: village(), cloud: darkCloud(4),
    cake: [380, 320, 260, 200].map((w, i) => cakeLayer(w, i + 3)), plate: cakePlate(), wine: winePot(),
    elder: figure({ robe: INK.ink3, beard: true, staff: true, seed: 3 }), hero: figure({ robe: INK.azure, seed: 5 }),
    fam: [figure({ robe: INK.azure, bag: true, seed: 6 }), figure({ robe: INK.ochre, bag: true, seed: 7 }), figure({ robe: INK.green2, bag: true, seed: 8 })],
    famCup: [figure({ robe: INK.azure, bag: true, cup: true, seed: 6 }), figure({ robe: INK.ochre, bag: true, cup: true, seed: 7 }), figure({ robe: INK.green2, bag: true, cup: true, seed: 8 })],
    oldMan: figure({ robe: INK.ink3, beard: true, bend: 1, seed: 12 }), oldWoman: figure({ robe: INK.ochre, bend: 1, seed: 13 }),
    youth: figure({ robe: INK.azure, flower: true, seed: 14 }),
  };
  SP.fans = [roundFan(mtn, '登高', 1), roundFan(chrysanthemum(21), '赏菊', 2), roundFan(zhuyu(23), '插茱萸', 3), roundFan(cakeStack, '吃重阳糕', 4)];
}
const P = (t, n, d = 0.5, ease = easeOut) => ease(prog(t, cue(n), d));
function label(g, text, x, y, a = 1, size = 42) {
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; g.font = `700 ${size}px NotoSerifSC`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = 8; g.strokeStyle = 'rgba(244,238,226,0.9)'; g.strokeText(text, x, y);
  g.fillStyle = INK.ink; g.fillText(text, x, y); g.restore();
}
function draw(g, sp, x, yBase, s = 1, a = 1) {
  if (a <= 0) return;
  g.globalAlpha = a; g.drawImage(sp, x - sp.width * s / 2, yBase - sp.height * s, sp.width * s, sp.height * s); g.globalAlpha = 1;
}

const SCENES = {
  intro(g, ox, t) {
    draw(g, SP.mtn, ox + 360, 1300, 0.85, 0.95);
    draw(g, SP.pav, ox + 360 + (520 - 450) * 0.85, 1300 - (900 - 250) * 0.85 + 8, 0.6);
    const gx = ox + 760 - (t - cue('intro.geese')) * 95;
    if (t >= cue('intro.geese')) geese(g, gx, 560, t, 7, 1);
    brushText(g, '重阳节', ox - 90, 760, 210, prog(t, cue('intro.title') - 0.05, 1.0));
    stamp(g, '九月初九', ox + 300, 760, t - cue('intro.seal'), { size: 150 });
    splash(g, ox + 300, 760, t - cue('intro.seal'), { color: INK.red, rad: 120, seed: 3 });
    stamp(g, '答题', ox - 340, 980, t - cue('intro.hint'), { size: 120, rot: 0.06 });
  },
  a1(g, ox, t) {
    brushText(g, '九', ox - 90, 760, 470, prog(t, cue('a1.nine1') - 0.1, 0.55));
    const n2 = cue('a1.nine2');
    if (t >= n2 - 0.45) {
      const k = easeIn(prog(t, n2 - 0.45, 0.45));
      brushText(g, '九', lerp(ox + 700, ox + 90, k), 760, 470, 1, { color: '#7A7068', alpha: 0.85 });
    }
    splash(g, ox, 760, t - n2, { rad: 260, seed: 9 });
    brushText(g, '重阳', ox, 1130, 170, prog(t, cue('a1.name') - 0.05, 0.7), { color: INK.red });
  },
  jiujiu(g, ox, t) {
    draw(g, SP.pine, ox + 300, 1270, 0.95, clamp01(prog(t, TL.shot.jiujiu.t0 - 0.6, 1.2)));
    const m = cue('jiujiu.morph');
    const k = clamp01((t - (m - 0.15)) / 0.4);
    const blur = 6 * Math.sin(Math.PI * k);
    g.save(); g.filter = `blur(${blur.toFixed(2)}px)`;
    if (k < 1) brushText(g, '九九', ox - 200, 760, 240, 1, { alpha: 1 - k });
    if (k > 0) brushText(g, '久久', ox - 200, 760, 240, 1, { alpha: k, color: INK.ink });
    g.restore();
    splash(g, ox - 200, 760, t - m, { rad: 200, seed: 13, color: INK.ink2 });
    const c = cue('jiujiu.crane');
    const bx = ox + 300 + 0.45 * 560 * 0.95 - 40, by = 1270 - 0.6 * 720 * 0.95 + 18;
    if (t < c) {
      const u = easeInOut(prog(t, c - 2.2, 2.2));
      const x = lerp(ox - 700, bx, u), y = lerp(430, by - 150, u) - Math.sin(Math.PI * u) * 120;
      g.save(); g.translate(x, y); const s = 0.8 + 0.2 * Math.sin(t * 6);
      g.scale(0.85, 0.85 * s); g.drawImage(SP.craneFly, -SP.craneFly.width / 2, -SP.craneFly.height / 2); g.restore();
    } else draw(g, SP.craneStand, bx, by, 0.7);
  },
  han(g, ox, t) {
    draw(g, SP.palace, ox, 730, 1.0, clamp01(prog(t, TL.shot.han.t0 - 0.5, 1.0)));
    const items = [['han.zhuyu', SP.zhuyuS, -320, '茱萸'], ['han.cake', SP.plate, 0, '蓬饵'], ['han.wine', SP.wine, 320, '菊花酒']];
    for (const [n, sp, dx, txt] of items) {
      const k = prog(t, cue(n) - 0.35, 0.45);
      reveal(g, sp, ox + dx, 1110, k, { s: 0.95 });
      label(g, txt, ox + dx, 1160, easeOut(prog(t, cue(n), 0.3)));
    }
  },
  legend(g, ox, t) {
    draw(g, SP.village, ox + 150, 1210, 1.0);
    const c = cue('legend.cloud');
    const k = easeOut(prog(t, c - 0.8, 0.8));
    draw(g, SP.cloud, lerp(ox - 900, ox + 150, k), 1020, 0.95, k * 0.95);
    draw(g, SP.elder, ox - 320, 1250, 1.0);
    draw(g, SP.hero, ox - 160, 1250, 0.95);
    label(g, '费长房', ox - 320, 1278, 1, 34);
    label(g, '桓景', ox - 160, 1278, 1, 34);
    const p = prog(t, cue('legend.point') - 0.2, 0.6);
    if (p > 0) {
      g.save(); g.setLineDash([14, 14]); g.strokeStyle = rgba(INK.red, 0.85); g.lineWidth = 5;
      g.beginPath(); g.moveTo(ox - 280, 980); g.quadraticCurveTo(ox, 820, lerp(ox - 280, ox + 420, p), lerp(980, 640, p)); g.stroke(); g.restore();
      label(g, '登高！', ox + 420, 600, easeOut(prog(t, cue('legend.point') + 0.3, 0.3)), 48);
    }
  },
  a2(g, ox, t) {
    const mx = ox + 120, mb = 1300;
    draw(g, SP.village, ox - 330, 1310, 0.55);
    draw(g, SP.cloud, ox - 330, 1170, 0.55, 0.9 * (1 - prog(t, cue('a2.top'), 1.2)));
    draw(g, SP.mtn, mx, mb, 1.0);
    draw(g, SP.pav, mx - 450 + 520, mb - 900 + 262, 0.6);
    const cl = cue('a2.climb'), top = cue('a2.top');
    SP.fam.forEach((sp, i) => {
      const u = easeInOut(prog(t, cl + i * 0.25, top - cl - 0.5)) * (0.93 - i * 0.04);
      const [px, py] = SP.mtn.pathPoint(u);
      const done = t >= top;
      draw(g, done ? SP.famCup[i] : sp, mx - 450 + px, mb - 900 + py + 4, 0.62 + (1 - u) * 0.1);
    });
  },
  tang(g, ox, t) {
    const s = cue('tang.scroll');
    const k = easeOut(prog(t, s - 0.2, 0.8));
    const x0 = ox - 260, top = 380, hh = 840 * k;
    if (k > 0) {
      g.fillStyle = INK.silk; g.fillRect(x0 - 26, top, 572, hh);
      g.fillStyle = '#F8F1E2'; g.fillRect(x0, top + 30, 520, Math.max(0, hh - 60));
      stroke(g, [[x0 - 46, top], [x0 + 566, top]], 22, { seed: 2, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
      stroke(g, [[x0 - 46, top + hh], [x0 + 566, top + hh]], 22, { seed: 3, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
      g.save(); g.beginPath(); g.rect(x0, top, 520, hh); g.clip();
      brushText(g, '遥知兄弟登高处', ox + 100, 470, 84, prog(t, s + 0.4, 2.0), { vertical: true, align: 'start' });
      brushText(g, '遍插茱萸少一人', ox - 20, 470, 84, prog(t, s + 1.5, 2.0), { vertical: true, align: 'start' });
      brushText(g, '王维', ox - 150, 900, 56, prog(t, s + 2.6, 0.6), { vertical: true, align: 'start', color: INK.ink2 });
      g.restore();
      stamp(g, '摩诘', ox - 150, 1080, t - (s + 3.2), { size: 80, rot: 0 });
    }
    draw(g, SP.zhuyu, ox + 360, 1300, 0.75);
  },
  a3(g, ox, t) {
    const r = cue('a3.reveal');
    const times = [r + 0.55, cue('a3.l2'), cue('a3.l3'), cue('a3.l4')];
    const base = 1240;
    SP.cake.forEach((sp, i) => {
      const d = t - times[i];
      if (d < -0.25) return;
      const y = base - i * 70 + 20 - (d < 0 ? (-d / 0.25) * 320 : 0);
      const sq = d >= 0 ? 1 + 0.08 * Math.exp(-d * 14) * Math.cos(d * 40) : 1;
      g.save(); g.translate(ox - 80, y); g.scale(1 / sq, sq);
      g.drawImage(sp, -sp.width / 2, -sp.height); g.restore();
    });
    const l4 = cue('a3.l4');
    if (t >= l4) {
      const fy = base - 4 * 70 + 50;
      stroke(g, [[ox - 80, fy], [ox - 80, fy - 120]], 6, { seed: 4, dry: 0, color: '#5A4632' });
      g.fillStyle = INK.red; g.beginPath(); g.moveTo(ox - 78, fy - 120); g.lineTo(ox + 10 + Math.sin(t * 5) * 6, fy - 100); g.lineTo(ox - 78, fy - 80); g.fill();
    }
    brushText(g, '步步高', ox + 320, 660, 130, prog(t, l4, 0.8), { vertical: true, align: 'start', color: INK.red });
  },
  customs(g, ox, t) {
    const pos = [[-225, 560], [225, 560], [-225, 1010], [225, 1010]];
    ['customs.i1', 'customs.i2', 'customs.i3', 'customs.i4'].forEach((n, i) => {
      const k = easeOutBack(prog(t, cue(n) - 0.15, 0.4), 1.5);
      if (k <= 0) return;
      const sp = SP.fans[i], s = 0.92 * k;
      g.save(); g.globalAlpha = clamp01(k * 2); g.translate(ox + pos[i][0], pos[i][1]); g.scale(s, s); g.rotate((1 - k) * 0.3);
      g.drawImage(sp, -sp.width / 2, -180); g.restore();
    });
  },
  a4(g, ox, t) {
    draw(g, SP.pine2, ox - 300, 1260, 0.9);
    draw(g, SP.oldMan, ox - 90, 1260, 0.95);
    draw(g, SP.oldWoman, ox + 40, 1260, 0.92);
    const yk = easeOut(prog(t, cue('a4.reveal') + 0.4, 1.2));
    draw(g, SP.youth, lerp(ox + 420, ox + 200, yk), 1260, 0.95);
    brushText(g, '敬老', ox + 380, 600, 140, prog(t, cue('a4.reveal') + 0.8, 0.8), { vertical: true, align: 'start' });
    const f = cue('a4.final');
    stamp(g, '重阳', ox + 380, 960, t - f, { size: 150, rot: 0.05 });
    splash(g, ox + 380, 960, t - f, { color: INK.red, rad: 170, seed: 21 });
  },
};

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
  TL.quiz.forEach((q, qi) => {
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
let ctx = null, PAPER = null;
function frame(t, si) {
  const g = ctx;
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.drawImage(PAPER, 0, 0);
  const cx = camX(t);
  const [sx, sy] = shakeAt(t);
  g.setTransform(1, 0, 0, 1, sx, sy);
  const S = TL.shot;
  // 开篇红日（远景视差）
  const sunX = W / 2 - 230 - (cx - S.intro.x) * 0.15, sunA = 1 - prog(cx - S.intro.x, 600, 1400);
  if (sunA > 0) { blot(g, sunX, 520, 190, INK.red2, 0.18 * sunA); g.fillStyle = rgba(INK.red, 0.82 * sunA); g.beginPath(); g.arc(sunX, 520, 76, 0, Math.PI * 2); g.fill(); }
  mountains(g, 'far', cx);
  mist(g, 900, 260, t, cx, 0.3, 0.75, 3);
  mountains(g, 'mid', cx);
  mist(g, 1160, 300, t, cx, 0.55, 0.85, 7);
  for (const s of TL.shots) {
    const ox = s.x - cx + W / 2;
    if (ox < -1200 || ox > W + 1200) continue;
    const f = SCENES[s.name];
    if (f) f(g, ox, t);
  }
  mist(g, 1330, 260, t, cx, 1.0, 0.55, 11);
  const fade = g.createLinearGradient(0, 1250, 0, 1620);       // 字幕区淡去，让文字干净
  fade.addColorStop(0, 'rgba(241,232,214,0)'); fade.addColorStop(1, 'rgba(241,232,214,0.85)');
  g.fillStyle = fade; g.fillRect(-40, 1250, W + 80, 700);
  drawCard(g, t);
  g.setTransform(1, 0, 0, 1, 0, 0);
  const veil = Math.max(1 - clamp01(t / 0.5), clamp01((t - (TL.end - 1.1)) / 1.0));
  if (veil > 0) { g.fillStyle = `rgba(239,230,211,${veil})`; g.fillRect(0, 0, W, H); }
  drawUI(t, si);
}

async function boot() {
  Object.assign(TL, await (await fetch('./timeline.json')).json());
  TL.shot = {};
  TL.shots.forEach((s, i) => { s.x = i * SPAN; TL.shot[s.name] = s; });
  KEYS = [[0, -160]];
  TL.shots.forEach((s, i) => { if (i) KEYS.push([s.t0 + 1.0, s.x - 40]); KEYS.push([s.t1 - 0.35, s.x + 40]); });
  KEYS.push([TL.end + 1, TL.shots[TL.shots.length - 1].x + 60]);
  for (const f of ['66px MaShanZheng', '700 60px NotoSerifSC', '500 30px NotoSansSC', '700 30px NotoSansSC']) await document.fonts.load(f, '重阳节九');
  const c = document.getElementById('c');
  ctx = c.getContext('2d');
  PAPER = canvas(W, H); paintPaper(PAPER.getContext('2d'));
  CARD = cardSprite();
  buildSprites();
  warmMountains(-1200, TL.shots[TL.shots.length - 1].x + 1200);
  window.AC.ready = true;
}

const shotIndex = t => { for (let i = TL.shots.length - 1; i >= 0; i--) if (t >= TL.shots[i].t0) return i; return 0; };
window.AC = {
  ready: false,
  seek(t) { const i = shotIndex(t); frame(t, i); return i; },
  info() { return { shots: TL.shots.length, end: TL.end }; },
};
boot().catch(e => { window.AC.error = String(e && e.stack || e); console.error(e); });
