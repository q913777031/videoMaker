// 《春节是怎么来的？》各镜小景；长卷镜头、答题卡、字幕复用 chongyang/web/scroll.js，节庆小景来自 festive.js。
import {
  W, INK, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, rgba,
  brushText, stamp, splash, blot, stroke, figure, village, climbMountain,
} from '../../chongyang/web/ink.js';
import {
  door, firecrackers, firework, calPage, lantern, redEnvelope, coinString, nianBeast, bonfire, dinnerTable,
} from '../../chongyang/web/festive.js';
import { TL, cue, label, draw, runScroll } from '../../chongyang/web/scroll.js';

let SP = {};
function buildSprites() {
  SP = {
    mtn: climbMountain(), village: village(), beast: nianBeast(5), table: dinnerTable(),
    doorRed: door({ couplets: null, fu: false }), doorBare: door({ couplets: null, fu: false }),
    doorCouplet: door({ couplets: ['新年纳余庆', '嘉节号长春'], fu: false }),
    cal1914: calPage('民国三年', '1914', '春节'),
    villagers: [figure({ robe: INK.azure, seed: 51 }), figure({ robe: INK.ochre, seed: 52 })],
    elder: figure({ robe: INK.ink3, beard: true, bend: 1, seed: 61 }), child: figure({ robe: INK.red2, s: 0.7, seed: 62 }),
    fam: [figure({ robe: INK.ink3, beard: true, seed: 71 }), figure({ robe: INK.ochre, seed: 72 }), figure({ robe: INK.azure, seed: 73 }),
      figure({ robe: INK.red2, s: 0.75, seed: 74 })],
    famA: [figure({ robe: INK.azure, seed: 81 }), figure({ robe: INK.red2, s: 0.8, seed: 82 }), figure({ robe: INK.ochre, seed: 83 })],
  };
}

const drop = (t, t0, from = -500, to = 0, d = 0.5) => {     // 从上方落下并轻弹
  const dt = t - t0;
  if (dt < -d) return null;
  return dt < 0 ? lerp(from, to, easeIn(1 + dt / d)) : to + 16 * Math.exp(-dt * 8) * Math.cos(dt * 22);
};
function fuDiamond(g, x, y, k, upside = true) {
  if (k <= 0) return;
  g.save(); g.translate(x, y); g.scale(k, k);
  g.save(); g.rotate(Math.PI / 4); g.fillStyle = INK.red; g.fillRect(-60, -60, 120, 120); g.restore();
  if (upside) g.rotate(Math.PI);
  g.fillStyle = '#1E1B19'; g.font = '96px MaShanZheng'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('福', 0, 4);
  g.restore();
}
function hangText(g, x, y0, text, size, color, bg, alpha = 1, h = 504) {
  g.save(); g.globalAlpha = alpha;
  g.fillStyle = bg; g.fillRect(x - 36, y0, 72, h);
  g.strokeStyle = rgba(INK.ink, 0.6); g.lineWidth = 2; g.strokeRect(x - 36, y0, 72, h);
  g.fillStyle = color; g.font = `${size}px MaShanZheng`; g.textAlign = 'center'; g.textBaseline = 'middle';
  const step = h / text.length;
  [...text].forEach((ch, i) => g.fillText(ch, x, y0 + step * (i + 0.5)));
  g.restore();
}

const SCENES = {
  intro(g, ox, t) {
    draw(g, SP.mtn, ox + 380, 1300, 0.8, 0.95);
    [[-330, 300, 0], [-150, 230, 0.2], [330, 280, 0.35]].forEach(([dx, y, lag], i) => {
      const yy = drop(t, cue('intro.lanterns') + 0.6 + lag, -500, 0, 0.6);
      if (yy !== null) lantern(g, ox + dx, y + yy, 0.8, 1, t, i);
    });
    brushText(g, '春节', ox - 80, 760, 260, prog(t, cue('intro.title') - 0.05, 0.9));
    stamp(g, '正月初一', ox + 250, 800, t - cue('intro.seal'), { size: 150 });
    splash(g, ox + 250, 800, t - cue('intro.seal'), { color: INK.red, rad: 120, seed: 3 });
    stamp(g, '答题', ox - 330, 990, t - cue('intro.hint'), { size: 120, rot: 0.06 });
  },
  a1(g, ox, t) {
    const fx = ox - 80, fy = 1170;
    const fa = clamp01(prog(t, TL.shot.a1.t0 - 0.6, 1.0));
    if (fa > 0) { g.globalAlpha = fa; bonfire(g, fx, fy, t, 1.2); g.globalAlpha = 1; }
    const toss = cue('a1.toss'), pop = cue('a1.pop');
    if (t >= toss - 0.1 && t < pop) {
      const u = easeIn(prog(t, toss - 0.1, pop - toss + 0.1));
      const x = lerp(ox + 360, fx + 10, u), y = lerp(520, fy - 90, u) - Math.sin(Math.PI * u) * 120;
      g.save(); g.translate(x, y); g.rotate(u * 3);
      stroke(g, [[-80, 0], [80, 0]], 34, { color: INK.green2, seed: 3, dry: 2, taper: [0.02, 0.02] });
      for (const k of [-40, 0, 40]) stroke(g, [[k, -18], [k, 18]], 6, { color: INK.green, seed: 4 + k, dry: 0 });
      g.restore();
    }
    splash(g, fx, fy - 120, t - pop, { color: INK.gold, rad: 260, seed: 7, n: 22, dur: 0.9 });
    splash(g, fx, fy - 120, t - pop, { color: INK.red, rad: 200, seed: 9, n: 14, dur: 0.9 });
    const kp = easeOutBack(prog(t, pop, 0.3), 2.4);
    if (kp > 0) { g.save(); g.translate(ox + 60, 700); g.scale(kp, kp); brushText(g, '噼啪！', 0, 0, 140, 1, { color: INK.red }); g.restore(); }
    const sy = drop(t, cue('a1.string'), -700, 0, 0.5);
    if (sy !== null) firecrackers(g, ox + 360, 360 + sy, t, 13);
  },
  nian(g, ox, t) {
    draw(g, SP.village, ox + 200, 1230, 1.0);
    const b = cue('nian.beast'), sc = cue('nian.scare');
    let bx = lerp(ox + 760, ox + 130, easeOut(prog(t, b - 0.5, 1.1)));
    if (t > sc + 0.3) bx += easeIn(prog(t, sc + 0.3, 1.4)) * 900;
    const flip = t > sc + 0.3 ? -1 : 1;
    g.save(); g.translate(bx, 1180); g.scale(0.85 * flip, 0.85);
    g.drawImage(SP.beast, -SP.beast.width / 2, -SP.beast.height); g.restore();
    SP.villagers.forEach((sp, i) => draw(g, sp, ox - 330 + i * 140, 1260, 0.95));
    const fk = prog(t, sc - 0.4, 0.4);
    if (fk > 0) {
      g.save(); g.translate(ox - 270, 940); g.rotate(-0.3 + Math.sin(t * 8) * 0.2 * fk);
      stroke(g, [[0, 0], [0, -200]], 7, { color: '#5A4632', seed: 4, dry: 0 });
      g.fillStyle = rgba(INK.red, 0.92); g.beginPath(); g.moveTo(0, -200); g.quadraticCurveTo(80, -190 + Math.sin(t * 9) * 20, 150, -170);
      g.lineTo(140, -90); g.quadraticCurveTo(70, -110, 0, -110); g.closePath(); g.fill(); g.restore();
    }
    splash(g, ox - 60, 1100, t - sc, { color: INK.red, rad: 230, seed: 11, n: 20 });
    splash(g, ox - 60, 1100, t - sc, { color: INK.gold, rad: 180, seed: 13, n: 14 });
    const kb = easeOutBack(prog(t, sc, 0.3), 2.4);
    if (kb > 0 && t < sc + 2) { g.save(); g.translate(ox + 120, 640); g.scale(kb, kb); brushText(g, '砰！', 0, 0, 130, 1, { color: INK.red }); g.restore(); }
  },
  red(g, ox, t) {
    draw(g, SP.doorRed, ox, 1260, 0.9, clamp01(prog(t, TL.shot.red.t0 - 0.6, 1.0)));
    lantern(g, ox - 330, 330, 0.85, prog(t, cue('red.l1'), 0.3), t, 1);
    lantern(g, ox + 330, 330, 0.85, prog(t, cue('red.l2'), 0.3), t, 2);
    fuDiamond(g, ox, 1251 - 390 * 0.9, easeOutBack(prog(t, cue('red.fu') - 0.1, 0.35), 2), true);
    label(g, '倒“福”＝福到', ox, 1290, easeOut(prog(t, cue('red.fu') + 0.4, 0.3)), 40);
  },
  door(g, ox, t) {
    draw(g, SP.doorBare, ox, 1260, 0.9, clamp01(prog(t, TL.shot.door.t0 - 0.6, 1.0)));
    const blink = 0.5 + 0.5 * Math.sin((t - cue('door.door')) * 8);
    g.save(); g.setLineDash([16, 12]); g.strokeStyle = rgba(INK.red, 0.4 + 0.5 * blink); g.lineWidth = 5;
    for (const sx of [-1, 1]) g.strokeRect(ox + sx * 234 - 36, 720, 72, 504);
    g.restore();
    for (const sx of [-1, 1]) label(g, '?', ox + sx * 234, 972, 0.6 + 0.4 * blink, 70);
  },
  a2(g, ox, t) {
    const cp = cue('a2.couplet');
    const m = clamp01((t - (cp - 0.1)) / 0.5);
    draw(g, SP.doorBare, ox, 1260, 0.9, 1 - m);
    draw(g, SP.doorCouplet, ox, 1260, 0.9, m);
    const by = drop(t, cue('a2.boards'), -600, 0, 0.45);
    if (by !== null && m < 1) {
      hangText(g, ox + 234, 720 + by, '神荼', 70, '#2A2622', '#C49A6C', 1 - m);
      hangText(g, ox - 234, 720 + by, '郁垒', 70, '#2A2622', '#C49A6C', 1 - m);
    }
    label(g, '桃符', ox, 640, easeOut(prog(t, cue('a2.boards') + 0.3, 0.3)) * (1 - m), 50);
    label(g, '春联', ox, 640, m, 50);
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
      brushText(g, '千门万户曈曈日', ox + 100, 470, 84, prog(t, s + 0.4, 2.0), { vertical: true, align: 'start' });
      brushText(g, '总把新桃换旧符', ox - 20, 470, 84, prog(t, s + 1.5, 2.0), { vertical: true, align: 'start' });
      brushText(g, '王安石', ox - 150, 880, 52, prog(t, s + 2.6, 0.6), { vertical: true, align: 'start', color: INK.ink2 });
      g.restore();
    }
    firecrackers(g, ox + 380, 380, t, 11);
  },
  a3(g, ox, t) {
    draw(g, SP.elder, ox - 200, 1260, 1.05);
    draw(g, SP.child, ox + 120, 1260, 1.05);
    const gv = cue('a3.give');
    const u = easeInOut(prog(t, gv - 0.4, 0.9));
    if (t >= gv - 0.4) redEnvelope(g, lerp(ox - 130, ox + 80, u), lerp(1080, 1100, u) - Math.sin(Math.PI * u) * 60, 0.8, -0.2 + u * 0.3);
    const cs = drop(t, cue('a3.coins'), -600, 0, 0.45);
    if (cs !== null) coinString(g, ox + 340, 560 + cs, t);
    brushText(g, '压祟', ox - 40, 700, 170, prog(t, cue('a3.reveal') + 0.6, 0.7), { color: INK.red });
  },
  customs(g, ox, t) {
    const cy = drop(t, cue('customs.cal'), -700, 0, 0.45);
    if (cy !== null) { g.save(); g.translate(ox - 280, 620 + cy); g.scale(0.62, 0.62); g.rotate(-0.05); g.drawImage(SP.cal1914, -SP.cal1914.width / 2, -SP.cal1914.height / 2); g.restore(); }
    brushText(g, '春节', ox + 190, 600, 170, prog(t, cue('customs.cal') + 0.3, 0.7));
    const fk = prog(t, cue('customs.family') - 0.3, 0.6);
    SP.fam.forEach((sp, i) => draw(g, sp, ox - 270 + i * 180, 1080, 0.85, fk));
    const tk = easeOutBack(prog(t, cue('customs.table') - 0.15, 0.4), 1.4);
    if (tk > 0) { g.save(); g.globalAlpha = clamp01(tk * 2); g.translate(ox, 1050); g.scale(tk, tk); g.drawImage(SP.table, -SP.table.width / 2, -120); g.restore(); }
  },
  a4(g, ox, t) {
    const fw = cue('a4.firework');
    firework(g, ox - 210, 560, t - fw, INK.red, 3);
    firework(g, ox + 170, 470, t - fw - 0.25, INK.gold, 7, 180);
    firework(g, ox + 330, 700, t - fw - 0.5, INK.red2, 11, 150);
    lantern(g, ox - 380, 280, 0.7, 1, t, 3);
    SP.famA.forEach((sp, i) => draw(g, sp, ox - 130 + i * 130, 1260, 0.9));
    brushText(g, '过年好', ox, 900, 150, prog(t, cue('a4.reveal') + 0.9, 0.9), { color: INK.red });
    stamp(g, '春节', ox + 320, 1080, t - cue('a4.final'), { size: 150, rot: 0.05 });
    splash(g, ox + 320, 1080, t - cue('a4.final'), { color: INK.red, rad: 170, seed: 21 });
  },
};

function sun(g, cx) {                                    // 开篇红日（远景视差）
  const x0 = TL.shot.intro.x;
  const sunX = W / 2 - 230 - (cx - x0) * 0.15, a = 1 - prog(cx - x0, 600, 1400);
  if (a <= 0) return;
  blot(g, sunX, 540, 190, INK.red2, 0.18 * a);
  g.fillStyle = rgba(INK.red, 0.82 * a); g.beginPath(); g.arc(sunX, 540, 76, 0, Math.PI * 2); g.fill();
}

runScroll({
  scenes: SCENES, sprites: buildSprites, backdrop: sun, fontSample: '春节福桃符',
  shakes: [['a1.reveal', 14], ['a1.pop', 12], ['nian.scare', 12], ['a4.final', 16]],
});
