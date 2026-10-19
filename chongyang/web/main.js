// 《重阳节是怎么来的？》各镜小景；长卷镜头、答题卡、字幕由 scroll.js 统一处理。
import {
  W, INK, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, canvas, rgba,
  brushText, stamp, splash, blot, reveal, stroke, pine, chrysanthemum, zhuyu, crane, figure, pavilion, palace, village, darkCloud,
  cakeLayer, cakePlate, winePot, climbMountain, geese, roundFan,
} from './ink.js';
import { TL, cue, label, draw, runScroll } from './scroll.js';

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


function sun(g, cx) {                                    // 开篇红日（远景视差）
  const x0 = TL.shot.intro.x;
  const sunX = W / 2 - 230 - (cx - x0) * 0.15, sunA = 1 - prog(cx - x0, 600, 1400);
  if (sunA <= 0) return;
  blot(g, sunX, 520, 190, INK.red2, 0.18 * sunA);
  g.fillStyle = rgba(INK.red, 0.82 * sunA); g.beginPath(); g.arc(sunX, 520, 76, 0, Math.PI * 2); g.fill();
}

runScroll({
  scenes: SCENES, sprites: buildSprites, backdrop: sun, fontSample: '重阳节九',
  shakes: [['a1.reveal', 14], ['a1.nine2', 10], ['legend.cloud', 8], ['a4.final', 16]],
});
