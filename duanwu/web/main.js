// 《端午节是怎么来的？》各镜小景（夏日江景水墨长卷）；长卷镜头、答题卡、字幕复用 chongyang/web/scroll.js，节庆小景来自 festive.js。
import {
  W, INK, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, rgba,
  brushText, stamp, splash, blot, stroke, figure,
} from '../../chongyang/web/ink.js';
import { door, river, dragonBoat, zongzi, herbBundle, sachet, colorRope } from '../../chongyang/web/festive.js';
import { TL, cue, label, draw, runScroll } from '../../chongyang/web/scroll.js';

let SP = {};
function buildSprites() {
  SP = {
    door: door({ couplets: null, fu: false }), fan: figure({ robe: INK.ochre, seed: 141 }),
    poet: figure({ robe: INK.ink3, s: 1.25, seed: 142 }),
  };
}
const RIVER_Y = 1060;
function mosquitoes(g, x, y, t, n, k, seed = 1) {         // 蚊虫：一团乱飞的小墨点，k 为可见度
  if (k <= 0) return;
  for (let i = 0; i < n; i++) {
    const a = t * (2 + (i % 5) * 0.4) + i * 1.7, r = 40 + (i * 37 % 110);
    const px = x + Math.cos(a) * r + Math.sin(a * 2.3) * 20, py = y + Math.sin(a * 1.3) * r * 0.6;
    g.fillStyle = rgba(INK.ink, 0.8 * k);
    g.beginPath(); g.arc(px, py, 3.5, 0, Math.PI * 2); g.fill();
    g.strokeStyle = rgba(INK.ink, 0.4 * k); g.lineWidth = 1;
    g.beginPath(); g.moveTo(px - 6, py - 3 + Math.sin(t * 40 + i) * 2); g.lineTo(px + 6, py - 3 - Math.sin(t * 40 + i) * 2); g.stroke();
  }
}
function talisman(g, x, y, k) {                           // 门上驱邪的朱砂符（红纸 + 墨笔划）
  if (k <= 0) return;
  g.save(); g.translate(x, y); g.scale(k, k);
  g.fillStyle = '#E2B34A'; g.fillRect(-45, -110, 90, 220);
  g.strokeStyle = rgba(INK.red, 0.95); g.lineWidth = 6;
  g.beginPath(); g.moveTo(-20, -80); g.lineTo(20, -80); g.moveTo(0, -80); g.lineTo(0, 80); g.moveTo(-25, -30); g.quadraticCurveTo(25, -10, -20, 20);
  g.moveTo(-20, 40); g.lineTo(25, 60); g.stroke();
  g.restore();
}

const SCENES = {
  intro(g, ox, t) {
    river(g, RIVER_Y, 220, t, ox);
    const b = cue('intro.boat');
    dragonBoat(g, lerp(ox + 700, ox - 900, (t - b) * 0.07), RIVER_Y + 70, t, 0.55, -1);
    herbBundle(g, ox + 400, 1280, 1.0, 'ai', 5);
    brushText(g, '端午', ox - 80, 760, 260, prog(t, cue('intro.title') - 0.05, 0.9));
    stamp(g, '五月初五', ox + 250, 800, t - cue('intro.seal'), { size: 150 });
    splash(g, ox + 250, 800, t - cue('intro.seal'), { color: INK.red, rad: 120, seed: 3 });
    stamp(g, '答题', ox - 330, 990, t - cue('intro.hint'), { size: 120, rot: 0.06 });
  },
  a1(g, ox, t) {
    brushText(g, '端', ox - 180, 760, 300, prog(t, cue('a1.duan') - 0.1, 0.55));
    brushText(g, '午', ox + 180, 760, 300, prog(t, cue('a1.wu') - 0.1, 0.55));
    label(g, '开头', ox - 180, 990, easeOut(prog(t, cue('a1.duan') + 0.4, 0.3)), 50);
    label(g, '同“五”', ox + 180, 990, easeOut(prog(t, cue('a1.wu') + 0.4, 0.3)), 50);
    brushText(g, '端五', ox, 1150, 150, prog(t, cue('a1.duanwu') - 0.05, 0.6), { color: INK.red });
  },
  eyue(g, ox, t) {
    const sk = clamp01(prog(t, cue('eyue.heat') - 0.3, 0.8));
    blot(g, ox + 300, 470, 220, '#F2A65A', 0.35 * sk);
    g.fillStyle = rgba(INK.red, 0.85 * sk); g.beginPath(); g.arc(ox + 300, 470, 80, 0, Math.PI * 2); g.fill();
    for (let i = 0; i < 12; i++) {
      const a = i / 12 * Math.PI * 2 + t * 0.3;
      stroke(g, [[ox + 300 + Math.cos(a) * 110, 470 + Math.sin(a) * 110], [ox + 300 + Math.cos(a) * 150, 470 + Math.sin(a) * 150]], 6, { color: INK.red2, alpha: 0.7 * sk, seed: i, dry: 0 });
    }
    draw(g, SP.door, ox - 120, 1250, 0.6);
    draw(g, SP.fan, ox + 220, 1260, 0.95);
    const w = cue('eyue.ward');
    talisman(g, ox - 120, 990, 0.7 * easeOutBack(prog(t, w - 0.1, 0.35), 2));
    const scatter = easeIn(prog(t, w, 1.2));
    mosquitoes(g, ox + lerp(0, 600, scatter), lerp(820, 500, scatter), t, 26, sk * (1 - scatter));
  },
  river(g, ox, t) {
    river(g, RIVER_Y, 240, t, ox);
    const k = clamp01(prog(t, TL.shot.river.t0 - 0.6, 1.0));
    g.save(); g.globalAlpha = k;
    stroke(g, [[ox - 520, RIVER_Y - 4], [ox - 60, RIVER_Y - 30], [ox + 120, RIVER_Y + 6]], 30, { seed: 3, dry: 4, color: '#4A3E34', taper: [0.02, 0.4] });
    draw(g, SP.poet, ox - 220, RIVER_Y - 20, 1.0);
    g.restore();
    const ks = easeOut(prog(t, cue('river.scroll') - 0.2, 0.6));
    if (ks > 0) {
      g.fillStyle = '#F8F1E2'; g.fillRect(ox + 20, 620, 360 * ks, 120);
      g.strokeStyle = rgba(INK.ink, 0.5); g.lineWidth = 3; g.strokeRect(ox + 20, 620, 360 * ks, 120);
      for (let i = 0; i < 6; i++) if (i / 6 < ks) stroke(g, [[ox + 330 - i * 52, 640], [ox + 330 - i * 52, 720]], 7, { seed: 40 + i, dry: 1, alpha: 0.7 });
      for (let i = 0; i < 6; i++) {
        const u = ((t - cue('river.scroll')) * 0.25 + i * 0.17) % 1;
        if (t < cue('river.scroll')) break;
        g.fillStyle = rgba(INK.ink, 0.6 * (1 - u)); g.font = '46px MaShanZheng'; g.textAlign = 'center';
        g.fillText('兮', ox + 120 + i * 50 + Math.sin(u * 6 + i) * 20, 600 - u * 220);
      }
    }
  },
  leap(g, ox, t) {
    river(g, RIVER_Y, 240, t, ox);
    const s = cue('leap.splash');
    for (let k = 0; k < 4; k++) {
      const d = t - s - k * 0.35;
      if (d < 0) continue;
      g.strokeStyle = rgba(INK.ink2, 0.6 * Math.max(0, 1 - d / 3)); g.lineWidth = 4;
      g.beginPath(); g.ellipse(ox, RIVER_Y + 90, 40 + d * 160, 12 + d * 40, 0, 0, Math.PI * 2); g.stroke();
    }
    splash(g, ox, RIVER_Y + 70, t - s, { color: INK.ink2, rad: 180, seed: 17, n: 18, dur: 0.9 });
    if (t < s) { g.fillStyle = INK.ink2; g.beginPath(); g.arc(ox, lerp(500, RIVER_Y + 70, easeIn(prog(t, s - 0.6, 0.6))), 30, 0, Math.PI * 2); g.fill(); }
  },
  a2(g, ox, t) {
    river(g, RIVER_Y, 240, t, ox);
    const bt = cue('a2.boats');
    const u = easeOut(prog(t, bt - 0.8, 1.6));
    dragonBoat(g, lerp(ox + 900, ox + 160, u), RIVER_Y + 60, t, 0.8, -1, 1);
    dragonBoat(g, lerp(ox - 900, ox - 220, u), RIVER_Y + 150, t, 0.7, 1, 2);
    const dr = cue('a2.drum');
    for (let k = 0; k < 3; k++) splash(g, ox + 160, RIVER_Y + 20, t - dr - k * 0.53, { color: INK.gold, rad: 60, seed: 30 + k, n: 8, dur: 0.4 });
    label(g, '咚', ox + 160, RIVER_Y - 120, easeOut(prog(t, dr, 0.2)) * (1 - prog(t, dr + 2, 0.4)), 60);
    const rc = cue('a2.rice');
    for (let i = 0; i < 4; i++) {
      const d = t - rc - i * 0.3;
      if (d < 0 || d > 1.6) continue;
      const x = ox + 60 + i * 60, y = lerp(RIVER_Y - 40, RIVER_Y + 110, easeIn(clamp01(d / 0.6)));
      g.fillStyle = '#7A9A5A'; g.fillRect(x - 10, y - 24, 20, 48);
      if (d > 0.6) splash(g, x, RIVER_Y + 110, d - 0.6, { color: INK.ink2, rad: 50, seed: 50 + i, n: 6, dur: 0.5 });
    }
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
      brushText(g, '节分端午自谁言', ox + 100, 470, 84, prog(t, s + 0.4, 2.0), { vertical: true, align: 'start' });
      brushText(g, '万古传闻为屈原', ox - 20, 470, 84, prog(t, s + 1.5, 2.0), { vertical: true, align: 'start' });
      brushText(g, '文秀', ox - 150, 900, 52, prog(t, s + 2.6, 0.6), { vertical: true, align: 'start', color: INK.ink2 });
      g.restore();
    }
    herbBundle(g, ox + 400, 1250, 0.8, 'ai', 9);
  },
  a3(g, ox, t) {
    draw(g, SP.door, ox, 1260, 0.9);
    const a = cue('a3.ai'), c = cue('a3.changpu');
    if (t > a - 0.3) herbBundle(g, ox - 260, 1240 + (t < a ? (a - t) * -600 : 0), 1.1, 'ai', 13);
    if (t > c - 0.3) herbBundle(g, ox + 260, 1240 + (t < c ? (c - t) * -600 : 0), 1.0, 'changpu', 15);
    label(g, '艾草', ox - 260, 1290, easeOut(prog(t, a + 0.2, 0.3)), 40);
    label(g, '菖蒲', ox + 260, 1290, easeOut(prog(t, c + 0.2, 0.3)), 40);
    const sc = easeIn(prog(t, c, 1.5));
    mosquitoes(g, ox + lerp(0, 700, sc), lerp(760, 380, sc), t, 22, 1 - sc, 3);
  },
  customs(g, ox, t) {
    river(g, RIVER_Y + 40, 220, t, ox);
    const zk = prog(t, cue('customs.zongzi') - 0.3, 0.5);
    if (zk > 0) {
      g.strokeStyle = INK.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(ox - 260, 360); g.lineTo(ox - 260, 360 + 420 * zk); g.stroke();
      for (let i = 0; i < 4; i++) if (i / 4 < zk) zongzi(g, ox - 260 + (i % 2 ? 26 : -26), 440 + i * 100, 0.85, (i % 2 ? 0.3 : -0.3));
    }
    const rk = easeOutBack(prog(t, cue('customs.rope') - 0.15, 0.4), 1.6);
    if (rk > 0) colorRope(g, ox + 140, 760, 1.6 * rk);
    if (rk > 0) sachet(g, ox + 330, 380, t, 0.9);
    const rc = cue('customs.race');
    if (t > rc - 1.0) {
      const u = (t - rc + 1.0) * 0.12;
      dragonBoat(g, lerp(ox + 800, ox - 500, u), RIVER_Y + 110, t, 0.6, -1, 3);
      dragonBoat(g, lerp(ox + 950, ox - 350, u * 0.95), RIVER_Y + 200, t, 0.55, -1, 4);
    }
  },
  a4(g, ox, t) {
    river(g, RIVER_Y, 240, t, ox);
    const r = cue('a4.reveal');
    for (let i = 0; i < 3; i++) dragonBoat(g, lerp(ox + 700 + i * 120, ox - 700, (t - r) * 0.09), RIVER_Y + 60 + i * 70, t, 0.5, -1, 5 + i);
    brushText(g, '端午安康', ox, 760, 140, prog(t, cue('a4.words') - 0.1, 1.0), { color: INK.red });
    stamp(g, '端午', ox + 320, 940, t - cue('a4.final'), { size: 150, rot: 0.05 });
    splash(g, ox + 320, 940, t - cue('a4.final'), { color: INK.red, rad: 170, seed: 21 });
  },
};

function summerSky(g, cx) {                               // 开篇：江天一轮夏日（远景视差）
  const x0 = TL.shot.intro.x;
  const a = 1 - prog(cx - x0, 600, 1400);
  if (a <= 0) return;
  const x = W / 2 - 230 - (cx - x0) * 0.15;
  blot(g, x, 520, 190, INK.red2, 0.18 * a);
  g.fillStyle = rgba(INK.red, 0.82 * a); g.beginPath(); g.arc(x, 520, 76, 0, Math.PI * 2); g.fill();
}

runScroll({
  scenes: SCENES, sprites: buildSprites, backdrop: summerSky, fontSample: '端午五月初五屈原艾草',
  shakes: [['a1.reveal', 14], ['leap.splash', 10], ['a4.final', 16]],
});
