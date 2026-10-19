// 《清明节是怎么来的？》各镜小景（烟雨水墨长卷）；长卷镜头、答题卡、字幕复用 chongyang/web/scroll.js，节庆小景来自 festive.js。
import {
  W, H, INK, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, rgba,
  brushText, stamp, splash, blot, stroke, curve, figure, village, climbMountain, cakePlate, chrysanthemum,
} from '../../chongyang/web/ink.js';
import { door, calPage, willow, swallow, kite, rain } from '../../chongyang/web/festive.js';
import { TL, cue, label, draw, runScroll } from '../../chongyang/web/scroll.js';

let SP = {};
function buildSprites() {
  SP = {
    mtn: climbMountain(), village: village(), plate: cakePlate(), chry: chrysanthemum(31, { heads: 2 }),
    door: door({ couplets: null, fu: false }), cal: calPage('四月', '4–6', '清明'),
    farmer: figure({ robe: INK.ochre, seed: 111 }), hermit: figure({ robe: INK.ink3, seed: 112 }),
    mother: figure({ robe: INK.ochre, beard: false, bend: 1, s: 0.55, seed: 113 }),
    duke: figure({ robe: INK.red2, s: 1.1, seed: 114 }),
    tiny: [figure({ robe: INK.azure, s: 0.32, seed: 121 }), figure({ robe: INK.ochre, s: 0.32, seed: 122 }), figure({ robe: INK.ink3, s: 0.32, seed: 123 }),
      figure({ robe: INK.green2, s: 0.32, seed: 124 })],
    fam: [figure({ robe: INK.ink3, bend: 1, seed: 131 }), figure({ robe: INK.azure, bend: 1, seed: 132 }), figure({ robe: INK.ochre, s: 0.75, seed: 133 })],
    child: figure({ robe: INK.red2, s: 0.75, seed: 134 }),
  };
}
const drop = (t, t0, from = -600, d = 0.45) => {
  const dt = t - t0;
  if (dt < -d) return null;
  return dt < 0 ? lerp(from, 0, easeIn(1 + dt / d)) : 16 * Math.exp(-dt * 8) * Math.cos(dt * 22);
};
function hscroll(g, x, y, w, k, text, size = 90) {           // 横向小卷轴（禁火令等），k 为展开进度
  if (k <= 0) return;
  const wd = w * k;
  g.fillStyle = '#F8F1E2'; g.fillRect(x - wd / 2, y - 70, wd, 140);
  g.strokeStyle = rgba(INK.ink, 0.6); g.lineWidth = 3; g.strokeRect(x - wd / 2, y - 70, wd, 140);
  for (const sx of [-1, 1]) stroke(g, [[x + sx * wd / 2, y - 90], [x + sx * wd / 2, y + 90]], 20, { seed: 4 + sx, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
  g.save(); g.beginPath(); g.rect(x - wd / 2, y - 70, wd, 140); g.clip();
  brushText(g, text, x, y, size, clamp01(k * 1.4 - 0.3), { color: INK.red });
  g.restore();
}

const SCENES = {
  intro(g, ox, t) {
    willow(g, ox + 360, 1260, t, 0.95, 4);
    const s0 = cue('intro.swallows');
    for (let i = 0; i < 3; i++) {
      const u = (t - s0 - i * 0.4) * 0.22;
      if (u > 0 && u < 1.2) swallow(g, lerp(ox + 700, ox - 600, u), 520 + i * 60 - Math.sin(u * 5 + i) * 40, t, 1 - i * 0.15, i);
    }
    brushText(g, '清明', ox - 80, 780, 260, prog(t, cue('intro.title') - 0.05, 0.9));
    stamp(g, '四月初', ox + 250, 820, t - cue('intro.seal'), { size: 150 });
    splash(g, ox + 250, 820, t - cue('intro.seal'), { color: INK.red, rad: 120, seed: 3 });
    stamp(g, '答题', ox - 330, 1010, t - cue('intro.hint'), { size: 120, rot: 0.06 });
  },
  a1(g, ox, t) {
    const cx = ox - 40, cy = 720, R = 260;
    const kr = easeInOut(prog(t, cue('a1.ring') - 0.3, 0.9));
    if (kr > 0) {
      g.strokeStyle = rgba(INK.ink, 0.85); g.lineWidth = 7;
      g.beginPath(); g.arc(cx, cy, R, 0, -Math.PI * 2 * kr, true); g.stroke();
      for (let i = 0; i < 24; i++) {
        if (i / 24 > kr) break;
        const a = i / 24 * Math.PI * 2;
        g.lineWidth = i % 6 ? 3 : 6;
        g.beginPath(); g.moveTo(cx + Math.cos(a) * (R - 18), cy - Math.sin(a) * (R - 18)); g.lineTo(cx + Math.cos(a) * (R + 18), cy - Math.sin(a) * (R + 18)); g.stroke();
      }
      const L = [['春分', 0], ['夏至', 90], ['秋分', 180], ['冬至', 270]];
      for (const [n, d] of L) {
        const a = d / 180 * Math.PI;
        label(g, n, cx + Math.cos(a) * (R + 70), cy - Math.sin(a) * (R + 60), clamp01((kr - d / 360) * 4), 34);
      }
    }
    const s = cue('a1.sun');
    const ka = easeInOut(prog(t, s - 1.2, 1.2));
    if (t > s - 1.2) {
      const a = lerp(-Math.PI / 2, Math.PI / 12, ka);
      const x = cx + Math.cos(a) * R, y = cy - Math.sin(a) * R;
      blot(g, x, y, 70, INK.red2, 0.3);
      g.fillStyle = rgba(INK.red, 0.92); g.beginPath(); g.arc(x, y, 30, 0, Math.PI * 2); g.fill();
      if (t >= s) {
        const ql = Math.PI / 12;
        label(g, '清明', cx + Math.cos(ql) * (R + 90), cy - Math.sin(ql) * (R + 90), easeOutBack(prog(t, s, 0.3), 2), 46);
        splash(g, x, y, t - s, { color: INK.red, rad: 110, seed: 7, n: 12 });
      }
    }
    brushText(g, '节气', cx, cy, 110, prog(t, cue('a1.ring') + 0.4, 0.6), { color: INK.ink2 });
    const cy2 = drop(t, cue('a1.cal'), -800, 0.45);
    if (cy2 !== null) { g.save(); g.translate(ox + 300, 1110 + cy2); g.scale(0.5, 0.5); g.drawImage(SP.cal, -SP.cal.width / 2, -SP.cal.height / 2); g.restore(); }
  },
  name(g, ox, t) {
    const cl = prog(t, cue('name.clear') - 0.2, 1.5);
    blot(g, ox, 620, 480, '#FFFFFF', 0.45 * cl);
    for (let i = 0; i < 5; i++) stroke(g, [[ox - 460, 1090 + i * 42], [ox, 1084 + i * 42], [ox + 460, 1092 + i * 42]], 6, { seed: 40 + i, dry: 2, color: '#6B5A46', alpha: 0.55, taper: [0.05, 0.05] });
    const sp = cue('name.sprout');
    for (let i = 0; i < 5; i++) for (let j = 0; j < 9; j++) {
      const k = easeOutBack(prog(t, sp - 0.2 + (i + j) * 0.05, 0.3), 2);
      if (k <= 0) continue;
      const x = ox - 400 + j * 100 + (i % 2) * 50, y = 1086 + i * 42;
      stroke(g, [[x, y], [x - 14 * k, y - 22 * k]], 5, { color: INK.green2, seed: i * 9 + j, dry: 0, taper: [0.1, 0.5] });
      stroke(g, [[x, y], [x + 14 * k, y - 24 * k]], 5, { color: INK.green, seed: i * 9 + j + 3, dry: 0, taper: [0.1, 0.5] });
    }
    draw(g, SP.farmer, ox - 260, 1070, 0.95);
    stroke(g, [[ox - 200, 940], [ox - 120, 1060], [ox - 100, 1080]], 7, { color: '#5A4632', seed: 9, dry: 0 });
  },
  hanshi(g, ox, t) {
    const sx = ox - 180, sy = 1180;
    g.fillStyle = '#C9A57E'; g.fillRect(sx - 200, sy - 260, 400, 260);
    g.strokeStyle = rgba(INK.ink, 0.8); g.lineWidth = 5; g.strokeRect(sx - 200, sy - 260, 400, 260);
    g.fillStyle = '#2A2622'; g.beginPath(); g.arc(sx, sy - 70, 70, Math.PI, 0); g.lineTo(sx + 70, sy); g.lineTo(sx - 70, sy); g.fill();
    g.fillStyle = '#8E857A'; g.fillRect(sx + 110, sy - 520, 60, 260);
    g.fillStyle = '#4A4440'; g.beginPath(); g.ellipse(sx - 40, sy - 270, 120, 26, 0, 0, Math.PI * 2); g.fill();
    const kx = prog(t, cue('hanshi.stove') - 0.1, 0.35);
    if (kx > 0) {
      stroke(g, [[sx - 90, sy - 150], [lerp(sx - 90, sx + 90, kx), lerp(sy - 150, sy + 10, kx)]], 16, { color: INK.red, seed: 3, dry: 1 });
      if (kx > 0.5) stroke(g, [[sx + 90, sy - 150], [lerp(sx + 90, sx - 90, (kx - 0.5) * 2), lerp(sy - 150, sy + 10, (kx - 0.5) * 2)]], 16, { color: INK.red, seed: 4, dry: 1 });
    }
    label(g, '冷灶', sx, sy - 330, easeOut(prog(t, cue('hanshi.stove') + 0.3, 0.3)), 46);
    const kf = easeOutBack(prog(t, cue('hanshi.food') - 0.15, 0.4), 1.6);
    if (kf > 0) {
      g.fillStyle = '#7A4A30'; g.fillRect(ox + 130, 1090, 300, 22); g.fillRect(ox + 150, 1110, 18, 140); g.fillRect(ox + 392, 1110, 18, 140);
      g.save(); g.translate(ox + 280, 1092); g.scale(kf * 0.8, kf * 0.8); g.drawImage(SP.plate, -SP.plate.width / 2, -SP.plate.height); g.restore();
      label(g, '冷食', ox + 280, 960, clamp01(kf), 46);
    }
  },
  hint(g, ox, t) {
    const k = clamp01(prog(t, TL.shot.hint.t0 - 0.6, 1.2));
    draw(g, SP.mtn, ox + 160, 1290, 1.0, k);
    if (k > 0) { g.globalAlpha = k; willow(g, ox - 280, 1260, t, 0.8, 9); g.globalAlpha = 1; }
    label(g, '绵山', ox + 200, 470, easeOut(prog(t, cue('hint.mountain') + 0.3, 0.4)), 54);
  },
  a2(g, ox, t) {
    const mx = ox + 160, mb = 1290;
    draw(g, SP.mtn, mx, mb, 1.0);
    const w0 = cue('a2.walk');
    const u = easeInOut(prog(t, w0, 5)) * 0.85;
    const [px, py] = SP.mtn.pathPoint(u);
    const hx = mx - 450 + px, hy = mb - 900 + py + 4, hs = 0.62 - u * 0.15;
    draw(g, SP.mother, hx - 18 * hs, hy - 150 * hs, hs * 1.4);
    draw(g, SP.hermit, hx, hy, hs);
    draw(g, SP.duke, ox - 300, 1260, 1.0);
    g.fillStyle = '#7A4A30'; g.fillRect(ox - 470, 1110, 120, 90);
    g.strokeStyle = INK.ink; g.lineWidth = 6; g.beginPath(); g.arc(ox - 410, 1220, 40, 0, Math.PI * 2); g.stroke();
    label(g, '介子推', hx, hy - 260 * hs - 30, easeOut(prog(t, w0 + 0.3, 0.3)), 40);
    label(g, '晋文公', ox - 300, 1290, 1, 36);
    hscroll(g, ox - 200, 760, 360, easeOut(prog(t, cue('a2.decree') - 0.2, 0.6)), '禁火');
  },
  poem(g, ox, t) {
    const s = cue('poem.scroll');
    const k = easeOut(prog(t, s - 0.2, 0.8));
    const x0 = ox - 260, top = 380, hh = 840 * k;
    if (k > 0) {
      g.fillStyle = INK.silk; g.fillRect(x0 - 26, top, 572, hh);
      g.fillStyle = '#F8F1E2'; g.fillRect(x0, top + 30, 520, Math.max(0, hh - 60));
      stroke(g, [[x0 - 46, top], [x0 + 566, top]], 22, { seed: 2, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
      stroke(g, [[x0 - 46, top + hh], [x0 + 566, top + hh]], 22, { seed: 3, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
      g.save(); g.beginPath(); g.rect(x0, top, 520, hh); g.clip();
      brushText(g, '清明时节雨纷纷', ox + 100, 470, 84, prog(t, s + 0.4, 2.0), { vertical: true, align: 'start' });
      brushText(g, '路上行人欲断魂', ox - 20, 470, 84, prog(t, s + 1.5, 2.0), { vertical: true, align: 'start' });
      brushText(g, '杜牧', ox - 150, 900, 52, prog(t, s + 2.6, 0.6), { vertical: true, align: 'start', color: INK.ink2 });
      g.restore();
    }
    willow(g, ox + 420, 1250, t, 0.6, 12);
  },
  a3(g, ox, t) {
    const top = 560, bot = 1200;
    g.fillStyle = INK.silk; g.fillRect(ox - 520, top - 20, 1040, bot - top + 40);
    g.fillStyle = '#EFE3C8'; g.fillRect(ox - 500, top, 1000, bot - top);
    g.save(); g.beginPath(); g.rect(ox - 500, top, 1000, bot - top); g.clip();
    g.fillStyle = 'rgba(110,130,140,0.35)';
    g.beginPath(); g.moveTo(ox - 520, 1040);
    for (let x = -520; x <= 520; x += 20) g.lineTo(ox + x, 1040 + Math.sin(x * 0.02 + t) * 6);
    g.lineTo(ox + 520, bot); g.lineTo(ox - 520, bot); g.closePath(); g.fill();
    g.drawImage(SP.village, ox - 760, 820, SP.village.width * 0.55, SP.village.height * 0.55);
    g.drawImage(SP.village, ox + 330, 820, SP.village.width * 0.55, SP.village.height * 0.55);
    const kb = easeInOut(prog(t, cue('a3.bridge') - 0.3, 0.8));
    if (kb > 0) {
      const pts = []; for (let i = 0; i <= 30; i++) { const u = i / 30; pts.push([ox - 330 + 660 * u, 1040 - Math.sin(Math.PI * u) * 200]); }
      stroke(g, pts.slice(0, Math.max(2, Math.round(31 * kb))), 30, { seed: 5, dry: 4, color: '#5A4632', taper: [0.02, 0.02] });
      if (kb >= 1) {
        for (let i = 0; i <= 12; i++) { const u = i / 12, x = ox - 330 + 660 * u, y = 1040 - Math.sin(Math.PI * u) * 200; stroke(g, [[x, y - 14], [x, y - 54]], 4, { seed: 20 + i, dry: 0, color: '#5A4632' }); }
        SP.tiny.forEach((sp, i) => {
          const u = ((t * 0.05 + i * 0.23) % 1) * 0.8 + 0.1, x = ox - 330 + 660 * u, y = 1040 - Math.sin(Math.PI * u) * 200 - 14;
          draw(g, sp, x, y, 1);
        });
      }
    }
    const bt = cue('a3.boat');
    if (t > bt - 1.2) {
      const bx = lerp(ox - 640, ox + 40, easeOut(prog(t, bt - 1.2, 1.2))) + Math.max(0, t - bt) * 20;
      g.fillStyle = '#6B4A30'; g.beginPath(); g.moveTo(bx - 170, 1080); g.quadraticCurveTo(bx, 1150, bx + 170, 1080); g.lineTo(bx + 140, 1110); g.lineTo(bx - 140, 1110); g.closePath(); g.fill();
      g.fillStyle = '#C9A57E'; g.fillRect(bx - 80, 1030, 160, 50);
      stroke(g, [[bx + 20, 1030], [bx + 20, 900]], 6, { seed: 31, dry: 0, color: '#5A4632' });
    }
    g.restore();
    label(g, '汴京 · 虹桥', ox, 520, easeOut(prog(t, cue('a3.bridge') + 0.3, 0.3)), 46);
  },
  customs(g, ox, t) {
    const tx = ox - 230;
    blot(g, tx, 1170, 170, INK.ink2, 0.35);
    g.fillStyle = rgba(INK.ink2, 0.75); g.beginPath(); g.ellipse(tx, 1190, 170, 90, 0, Math.PI, 0); g.fill();
    g.fillStyle = '#B8B2A6'; g.fillRect(tx - 40, 1000, 80, 170); g.strokeStyle = rgba(INK.ink, 0.7); g.lineWidth = 3; g.strokeRect(tx - 40, 1000, 80, 170);
    const kt = prog(t, cue('customs.tomb') - 0.3, 0.6);
    if (kt > 0) {
      draw(g, SP.chry, tx + 70, 1200, 0.35, kt);
      SP.fam.forEach((sp, i) => draw(g, sp, tx + 190 + i * 110, 1270, 0.8, kt));
    }
    const dx = ox + 330;
    draw(g, SP.door, dx, 1240, 0.5);
    const kw = prog(t, cue('customs.willow') - 0.2, 0.5);
    if (kw > 0) for (let i = 0; i < 5; i++) stroke(g, [[dx - 70 + i * 35, 932], [dx - 80 + i * 35 + Math.sin(t * 2 + i) * 6, 932 + 130 * kw]], 4, { color: INK.green2, seed: 50 + i, dry: 0, taper: [0.05, 0.5] });
    const kk = cue('customs.kite');
    draw(g, SP.child, ox + 160, 1270, 0.9);
    if (t > kk - 1.0) {
      const u = easeOut(prog(t, kk - 1.0, 1.4));
      kite(g, lerp(ox + 220, ox + 120, u), lerp(1100, 450, u), t, ox + 190, 1130, 0.9);
    }
  },
  a4(g, ox, t) {
    willow(g, ox - 380, 1260, t, 1.0, 21);
    brushText(g, '慎终追远', ox + 80, 820, 140, prog(t, cue('a4.words') - 0.1, 1.0));
    stamp(g, '清明', ox + 320, 1060, t - cue('a4.final'), { size: 150, rot: 0.05 });
    splash(g, ox + 320, 1060, t - cue('a4.final'), { color: INK.red, rad: 170, seed: 21 });
    for (let i = 0; i < 2; i++) swallow(g, ox + 200 + i * 120 - (t - cue('a4.reveal')) * 40, 520 + i * 50, t, 0.9, i);
  },
};

// 雨势：开篇细雨，“天清地明”处雨停，诗卷处再落，结尾雨歇
const RAIN = { intro: 1, q1: 0.6, a1: 0.25, name: 1, hanshi: 0, hint: 0.4, q2: 0.4, a2: 0.2, poem: 1, q3: 0.3, a3: 0, customs: 0, q4: 0.2, a4: 0.4 };
function rainLevel(t) {
  const sh = TL.shots;
  let i = sh.length - 1; while (i > 0 && t < sh[i].t0) i--;
  const cur = RAIN[sh[i].name] ?? 0, prev = i ? RAIN[sh[i - 1].name] ?? 0 : cur;
  let a = lerp(prev, cur, easeInOut(prog(t, sh[i].t0 - 0.5, 1.2)));
  if (sh[i].name === 'name') a *= 1 - prog(t, cue('name.clear') - 0.2, 1.5);
  if (sh[i].name === 'a4') a *= 1 - prog(t, cue('a4.reveal') + 0.5, 2);
  return a;
}
function overcast(g) {                                    // 阴天：顶部一层灰白云气
  const grd = g.createLinearGradient(0, 0, 0, 900);
  grd.addColorStop(0, 'rgba(120,128,132,0.20)'); grd.addColorStop(1, 'rgba(120,128,132,0)');
  g.fillStyle = grd; g.fillRect(-40, 0, W + 80, 900);
}

runScroll({
  scenes: SCENES, sprites: buildSprites, backdrop: overcast, overlay: (g, cx, t) => rain(g, t, rainLevel(t), W, H),
  fontSample: '清明寒食节气汴京', shakes: [['a1.reveal', 14], ['hint.mountain', 8], ['a4.final', 16]],
});
