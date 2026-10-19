// 《元宵节是怎么来的？》各镜小景（月夜水墨长卷）；长卷镜头、答题卡、字幕复用 chongyang/web/scroll.js，节庆小景来自 festive.js。
import {
  W, INK, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, rgba,
  brushText, stamp, splash, stroke, figure, village, palace,
} from '../../chongyang/web/ink.js';
import { firework, lantern, hangScroll, moon, tangyuanBowl, sieve } from '../../chongyang/web/festive.js';
import { TL, cue, label, draw, runScroll } from '../../chongyang/web/scroll.js';

let SP = {};
function buildSprites() {
  SP = {
    village: village(), palace: palace(),
    hang: [hangScroll('上元', '正月十五', 1), hangScroll('中元', '七月十五', 2), hangScroll('下元', '十月十五', 3)],
    walkers: [figure({ robe: INK.azure, seed: 91 }), figure({ robe: INK.ochre, seed: 92 }), figure({ robe: INK.red2, s: 0.8, seed: 93 }),
      figure({ robe: INK.green2, seed: 94 }), figure({ robe: INK.ink3, beard: true, seed: 95 })],
    reader: figure({ robe: INK.azure, seed: 96 }),
    fam: [figure({ robe: INK.azure, seed: 101 }), figure({ robe: INK.red2, s: 0.8, seed: 102 }), figure({ robe: INK.ochre, seed: 103 })],
  };
}
const drop = (t, t0, from = -600, d = 0.45) => {
  const dt = t - t0;
  if (dt < -d) return null;
  return dt < 0 ? lerp(from, 0, easeIn(1 + dt / d)) : 16 * Math.exp(-dt * 8) * Math.cos(dt * 22);
};
/** 提灯行人：sp 精灵，x 为脚底中心，手里一盏小灯笼。 */
function walker(g, sp, x, y, s, t, i) {
  draw(g, sp, x, y, s);
  lantern(g, x + 52 * s, y - 150 * s, 0.26 * s, 1, t, i);
}
/** 坊门：k=0 全关，1 全开（原点：门洞底部中心）。 */
function gate(g, ox, k, t, drumHit) {
  draw(g, SP.palace, ox, 640, 0.95);
  g.fillStyle = '#4A3A2E'; g.fillRect(ox - 430, 640, 860, 600);
  g.fillStyle = 'rgba(244,238,226,0.9)'; g.fillRect(ox - 230, 760, 460, 480);
  const dw = 230 * (1 - k);
  g.fillStyle = '#7A4A30';
  g.fillRect(ox - 230, 760, dw, 480); g.fillRect(ox + 230 - dw, 760, dw, 480);
  g.strokeStyle = rgba(INK.ink, 0.8); g.lineWidth = 4;
  g.strokeRect(ox - 230, 760, dw, 480); g.strokeRect(ox + 230 - dw, 760, dw, 480);
  for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) {
    g.fillStyle = '#C8A15E';
    if (dw > 40) { g.beginPath(); g.arc(ox - 230 + dw * (c + 0.5) / 3, 820 + r * 110, 7, 0, Math.PI * 2); g.fill();
      g.beginPath(); g.arc(ox + 230 - dw * (c + 0.5) / 3, 820 + r * 110, 7, 0, Math.PI * 2); g.fill(); }
  }
  const s = 1 + 0.15 * drumHit;
  g.save(); g.translate(ox - 340, 560); g.scale(s, s);
  g.fillStyle = INK.red; g.beginPath(); g.ellipse(0, 0, 70, 60, 0, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#E9D9B8'; g.beginPath(); g.ellipse(0, 0, 50, 44, 0, 0, Math.PI * 2); g.fill();
  g.restore();
}

const SCENES = {
  intro(g, ox, t) {
    [[-330, 300, 0], [-150, 230, 0.2], [330, 280, 0.35]].forEach(([dx, y, lag], i) => {
      const yy = drop(t, cue('intro.lanterns') + 0.6 + lag, -500, 0.6);
      if (yy !== null) lantern(g, ox + dx, y + yy, 0.8, 1, t, i);
    });
    brushText(g, '元宵', ox - 80, 780, 260, prog(t, cue('intro.title') - 0.05, 0.9));
    stamp(g, '正月十五', ox + 250, 820, t - cue('intro.seal'), { size: 150 });
    splash(g, ox + 250, 820, t - cue('intro.seal'), { color: INK.red, rad: 120, seed: 3 });
    stamp(g, '答题', ox - 330, 1010, t - cue('intro.hint'), { size: 120, rot: 0.06 });
  },
  a1(g, ox, t) {
    moon(g, ox, 780, 300, easeOut(prog(t, cue('a1.moon') - 0.2, 0.8)) * 0.9);
    splash(g, ox, 780, t - cue('a1.moon'), { color: INK.gold, rad: 360, seed: 5, n: 14 });
    brushText(g, '元', ox - 180, 780, 300, prog(t, cue('a1.yuan') - 0.1, 0.55));
    brushText(g, '宵', ox + 180, 780, 300, prog(t, cue('a1.xiao') - 0.1, 0.55));
    label(g, '正月', ox - 180, 1010, easeOut(prog(t, cue('a1.yuan') + 0.4, 0.3)), 50);
    label(g, '夜晚', ox + 180, 1010, easeOut(prog(t, cue('a1.xiao') + 0.4, 0.3)), 50);
  },
  sanyuan(g, ox, t) {
    ['sanyuan.s1', 'sanyuan.s2', 'sanyuan.s3'].forEach((n, i) => {
      const y = drop(t, cue(n), -1000, 0.35);
      if (y === null) return;
      const sp = SP.hang[i];
      g.drawImage(sp, ox + (i - 1) * 300 - sp.width / 2, 420 + y);
    });
    stamp(g, '元宵', ox - 300, 1080, t - cue('sanyuan.mark'), { size: 110, rot: -0.1 });
  },
  street(g, ox, t) {
    draw(g, SP.village, ox, 1240, 1.25);
    ['street.row1', 'street.row2', 'street.row3'].forEach((n, r) => {
      const lit = prog(t, cue(n) - 0.05, 0.25);
      for (let i = 0; i < 4; i++) lantern(g, ox - 390 + i * 260 + (r % 2) * 130, 300 + r * 150, 0.5 - r * 0.06, lit, t, r * 4 + i);
    });
    const c = cue('street.crowd');
    if (t > c - 0.6) SP.walkers.forEach((sp, i) => walker(g, sp, ox - 420 + i * 200 + (t - c) * 40, 1265, 0.8, t, i));
  },
  curfew(g, ox, t) {
    const d = cue('curfew.drum');
    gate(g, ox, 1 - easeInOut(prog(t, d, 1.2)), t, Math.exp(-Math.max(0, t - d) * 8) * (t >= d ? 1 : 0));
    const lk = prog(t, cue('curfew.lock') - 0.2, 0.3);
    if (lk > 0) stroke(g, [[lerp(ox - 400, ox - 260, lk), 990], [lerp(ox - 400, ox + 260, lk), 990]], 26, { color: '#3A2E26', seed: 3, dry: 1, taper: [0.02, 0.02] });
    label(g, '咚', ox - 340, 450, easeOut(prog(t, d, 0.2)) * (1 - prog(t, d + 1.2, 0.5)), 70);
  },
  a2(g, ox, t) {
    gate(g, ox, easeInOut(prog(t, cue('a2.open') - 0.2, 1.2)), t, 0);
    const f = cue('a2.flow');
    for (let i = 0; i < 10; i++) lantern(g, ox - 470 + i * 105, 300 + (i % 2) * 50, 0.42, prog(t, cue('a2.open') + i * 0.12, 0.3), t, i);
    if (t > f - 0.8) SP.walkers.forEach((sp, i) => {
      const u = clamp01((t - f + 0.8 - i * 0.25) / 4);
      if (u <= 0) return;
      const dir = i % 2 ? 1 : -1;
      walker(g, sp, ox + dir * (30 + u * (260 + i * 40)), 1240 + u * 30, 0.75 + u * 0.15, t, i);
    });
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
      brushText(g, '东风夜放花千树', ox + 100, 470, 84, prog(t, s + 0.4, 2.0), { vertical: true, align: 'start' });
      brushText(g, '更吹落星如雨', ox - 20, 470, 84, prog(t, s + 1.5, 2.0), { vertical: true, align: 'start' });
      brushText(g, '辛弃疾', ox - 150, 880, 52, prog(t, s + 2.6, 0.6), { vertical: true, align: 'start', color: INK.ink2 });
      g.restore();
    }
    lantern(g, ox + 380, 330, 0.6, 1, t, 7);
  },
  a3(g, ox, t) {
    const r = cue('a3.roll');
    sieve(g, ox - 60, 940, Math.max(0, t - r + 0.3) * 5, 1.1, easeOut(prog(t, r, 2.0)));
    brushText(g, '滚', ox - 60, 680, 170, prog(t, r, 0.5), { color: INK.red });
    const b = easeOutBack(prog(t, cue('a3.bowl') - 0.1, 0.4), 1.6);
    if (b > 0) { g.save(); g.globalAlpha = clamp01(b * 2); tangyuanBowl(g, ox + 290, 1190, t, 0.8 * b); g.restore(); }
  },
  riddle(g, ox, t) {
    ['riddle.slip1', 'riddle.slip2', 'riddle.slip3'].forEach((n, i) => {
      const x = ox - 300 + i * 300;
      lantern(g, x, 300, 0.7, 1, t, 10 + i);
      const y = drop(t, cue(n), -300, 0.35);
      if (y === null) return;
      const top = 540 + y;
      g.fillStyle = '#FBF3DF'; g.fillRect(x - 40, top, 80, 300);
      g.strokeStyle = rgba(INK.ink, 0.6); g.lineWidth = 2; g.strokeRect(x - 40, top, 80, 300);
      for (let k = 0; k < 4; k++) stroke(g, [[x - 6 + (k % 2) * 12, top + 30 + k * 50], [x - 6 + (k % 2) * 12, top + 60 + k * 50]], 8, { seed: i * 9 + k, dry: 0, alpha: 0.7 });
      g.fillStyle = INK.red; g.font = '64px MaShanZheng'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('谜', x, top + 260);
    });
    draw(g, SP.reader, ox + 40, 1270, 1.0);
    const gs = cue('riddle.guess');
    splash(g, ox + 40, 960, t - gs, { color: INK.gold, rad: 120, seed: 31, n: 12 });
    label(g, '猜到了！', ox + 40, 930, easeOutBack(prog(t, gs, 0.3), 2) * (t < gs + 3 ? 1 : 0), 48);
  },
  a4(g, ox, t) {
    moon(g, ox - 120, 560, 150, 1);
    const fw = cue('a4.firework');
    firework(g, ox + 220, 500, t - fw, INK.red, 3);
    firework(g, ox + 330, 720, t - fw - 0.3, INK.gold, 7, 160);
    SP.fam.forEach((sp, i) => walker(g, sp, ox - 150 + i * 150, 1265, 0.9, t, i));
    brushText(g, '元宵快乐', ox, 900, 130, prog(t, cue('a4.reveal') + 0.9, 0.9), { color: INK.red });
    stamp(g, '元宵', ox + 330, 1080, t - cue('a4.final'), { size: 150, rot: 0.05 });
    splash(g, ox + 330, 1080, t - cue('a4.final'), { color: INK.red, rad: 170, seed: 21 });
  },
};

function night(g, cx) {                                  // 月夜：顶部淡墨夜色；开篇远处一轮满月（慢视差）
  const grd = g.createLinearGradient(0, 0, 0, 1150);
  grd.addColorStop(0, 'rgba(52,60,74,0.30)'); grd.addColorStop(1, 'rgba(52,60,74,0)');
  g.fillStyle = grd; g.fillRect(-40, 0, W + 80, 1150);
  const x0 = TL.shot.intro.x;
  moon(g, 800 - (cx - x0) * 0.15, 470, 90, 0.95 * (1 - prog(cx - x0, 600, 1400)));
}

runScroll({
  scenes: SCENES, sprites: buildSprites, backdrop: night, fontSample: '元宵正月十五灯谜',
  shakes: [['a1.reveal', 14], ['curfew.drum', 10], ['a4.final', 16]],
});
