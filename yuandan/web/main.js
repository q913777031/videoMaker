// 《元旦是怎么来的？》各镜小景（冬日水墨长卷，飘雪）；长卷镜头、答题卡、字幕复用 chongyang/web/scroll.js。
import {
  W, H, INK, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, rng, canvas, rgba,
  brushText, stamp, splash, blot, stroke, curve, pine, figure, palace, climbMountain,
} from '../../chongyang/web/ink.js';
import { TL, cue, label, draw, runScroll } from '../../chongyang/web/scroll.js';

function sprite(w, h, f) { const c = canvas(w, h); f(c.getContext('2d'), w, h); return c; }

// ---------------------------------------------------------------- 本片小景
/** 红梅一枝（原点：枝根，向右下伸出）。 */
function plum(seed = 3) {
  return sprite(620, 520, (g) => {
    const r = rng(seed);
    const main = curve([[0, 30], [160, 70], [300, 60], [420, 140], [560, 170]], 6);
    stroke(g, main, 22, { seed, dry: 4, taper: [0.02, 0.6], color: '#3A2E26' });
    const tw = [];
    for (let i = 0; i < 6; i++) {
      const p = main[Math.floor(main.length * (0.15 + i * 0.13))];
      const e = [p[0] + 40 + r() * 70, p[1] + (r() < 0.5 ? -1 : 1) * (40 + r() * 80)];
      stroke(g, [p, [lerp(p[0], e[0], 0.5), lerp(p[1], e[1], 0.5) + 8], e], 7, { seed: seed + i, dry: 1, color: '#3A2E26' });
      tw.push(e, [lerp(p[0], e[0], 0.6), lerp(p[1], e[1], 0.6)]);
    }
    tw.push(main[main.length - 1], main[Math.floor(main.length * 0.5)]);
    for (const [x, y] of tw) {
      const n = 1 + Math.floor(r() * 2);
      for (let k = 0; k < n; k++) {
        const bx = x + (r() - 0.5) * 30, by = y + (r() - 0.5) * 24, R = 13 + r() * 6;
        for (let j = 0; j < 5; j++) {
          const a = j / 5 * Math.PI * 2 + r();
          g.fillStyle = rgba(INK.red2, 0.85);
          g.beginPath(); g.arc(bx + Math.cos(a) * R * 0.55, by + Math.sin(a) * R * 0.55, R * 0.5, 0, Math.PI * 2); g.fill();
        }
        g.fillStyle = INK.gold; g.beginPath(); g.arc(bx, by, 3, 0, Math.PI * 2); g.fill();
      }
    }
  });
}
/** 小挂轴：竖排大字 + 小字（原点：顶部中心）。 */
function hangScroll(big, small, seed = 1) {
  return sprite(220, 600, (g, w, h) => {
    g.fillStyle = INK.silk; g.fillRect(14, 10, w - 28, h - 30);
    g.fillStyle = '#F8F1E2'; g.fillRect(30, 50, w - 60, h - 110);
    stroke(g, [[0, 12], [w, 12]], 16, { seed, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
    stroke(g, [[4, h - 18], [w - 4, h - 18]], 18, { seed: seed + 1, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
    g.strokeStyle = rgba(INK.ink, 0.6); g.lineWidth = 2; g.beginPath(); g.moveTo(w / 2, 0); g.lineTo(w / 2 - 40, -40); g.lineTo(w / 2 + 40, -40); g.closePath();
    g.fillStyle = INK.ink; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.font = '120px MaShanZheng'; g.fillText(big, w / 2, 150);
    g.fillStyle = INK.red; g.font = '64px MaShanZheng';
    [...small].forEach((ch, i) => g.fillText(ch, w / 2, 280 + i * 70));
  });
}
/** 木门与春联（原点：底部中心）。 */
function door() {
  return sprite(760, 760, (g, w, h) => {
    const cx = w / 2, b = h - 10;
    g.fillStyle = '#7A4A30'; g.fillRect(cx - 200, b - 600, 400, 600);
    g.strokeStyle = rgba(INK.ink, 0.85); g.lineWidth = 5; g.strokeRect(cx - 200, b - 600, 400, 600);
    g.beginPath(); g.moveTo(cx, b - 600); g.lineTo(cx, b); g.stroke();
    for (const x of [-100, 100]) for (const y of [-470, -250]) { g.strokeStyle = 'rgba(40,24,16,0.6)'; g.lineWidth = 3; g.strokeRect(cx + x - 70, b + y - 80, 140, 160); }
    for (const x of [-26, 26]) { g.fillStyle = '#C8A15E'; g.beginPath(); g.arc(cx + x, b - 300, 14, 0, Math.PI * 2); g.fill(); }
    stroke(g, [[cx - 250, b - 610], [cx + 250, b - 610]], 30, { seed: 3, dry: 2, color: INK.ink, taper: [0.02, 0.02] });
    const couplet = (x, text) => {
      g.fillStyle = INK.red; g.fillRect(x - 40, b - 590, 80, 560);
      g.fillStyle = '#1E1B19'; g.font = '62px MaShanZheng'; g.textAlign = 'center'; g.textBaseline = 'middle';
      [...text].forEach((ch, i) => g.fillText(ch, x, b - 548 + i * 78));
    };
    couplet(cx + 260, '爆竹声中一岁除');
    couplet(cx - 260, '春风送暖入屠苏');
    g.fillStyle = INK.red; g.save(); g.translate(cx, b - 400); g.rotate(Math.PI / 4); g.fillRect(-70, -70, 140, 140); g.restore();
    g.fillStyle = '#1E1B19'; g.font = '110px MaShanZheng'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('福', cx, b - 396);
  });
}
/** 手撕日历一页（原点：中心）。 */
function calPage(top, big, bottom, { red = true, w = 380, h = 470 } = {}) {
  return sprite(w + 20, h + 20, (g) => {
    g.translate(10, 10);
    g.fillStyle = 'rgba(60,40,20,0.18)'; g.fillRect(8, 10, w, h);
    g.fillStyle = '#FBF6EC'; g.fillRect(0, 0, w, h);
    g.fillStyle = red ? INK.red : INK.ink2; g.fillRect(0, 0, w, 96);
    g.strokeStyle = rgba(INK.ink, 0.8); g.lineWidth = 4; g.strokeRect(0, 0, w, h);
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillStyle = '#FBF1E6'; g.font = '700 54px NotoSerifSC'; g.fillText(top, w / 2, 50);
    g.fillStyle = red ? INK.red : INK.ink; g.font = `700 ${big.length > 2 ? 88 : 200}px NotoSerifSC`; g.fillText(big, w / 2, 250);
    g.fillStyle = INK.ink; g.font = '64px MaShanZheng'; g.fillText(bottom, w / 2, h - 70);
    for (const x of [w * 0.3, w * 0.7]) { g.fillStyle = '#5A4632'; g.beginPath(); g.arc(x, 0, 10, 0, Math.PI * 2); g.fill(); }
  });
}
/** 水墨烟花：dt 秒后绽开并散落。 */
function firework(g, x, y, dt, color, seed, R = 210) {
  if (dt < 0 || dt > 2.6) return;
  const r = rng(seed);
  const k = easeOut(dt / 0.5), fade = 1 - clamp01((dt - 0.9) / 1.6);
  for (let i = 0; i < 26; i++) {
    const a = i / 26 * Math.PI * 2 + r() * 0.2, l = R * (0.75 + r() * 0.35) * k;
    const x1 = x + Math.cos(a) * l, y1 = y + Math.sin(a) * l + dt * dt * 22;
    const x0 = x + Math.cos(a) * l * 0.55, y0 = y + Math.sin(a) * l * 0.55;
    stroke(g, [[x0, y0], [lerp(x0, x1, 0.5), lerp(y0, y1, 0.5)], [x1, y1]], 7, { color, alpha: 0.85 * fade, seed: seed + i, dry: 0, taper: [0.6, 0.15] });
    g.fillStyle = rgba(INK.gold2, 0.9 * fade); g.beginPath(); g.arc(x1, y1, 4, 0, Math.PI * 2); g.fill();
  }
  blot(g, x, y, 70 * k, color, 0.25 * fade);
}

let SP = {};
function buildSprites() {
  SP = {
    plum: plum(3), plum2: plum(11), mtn: climbMountain(), pine: pine(5), palace: palace(),
    emperor: figure({ robe: '#2A2622', s: 1.3, seed: 31 }), door: door(),
    hang: [hangScroll('夏', '正月', 1), hangScroll('商', '十二月', 2), hangScroll('周', '十一月', 3)],
    calOld: calPage('十二月', '31', '除夕前', { red: false }), calNew: calPage('一月', '1', '新年'),
    calYuandan: calPage('公历', '1月1日', '元旦'), calChunjie: calPage('农历', '正月初一', '春节'),
    fam: [figure({ robe: INK.azure, seed: 41 }), figure({ robe: INK.red2, seed: 42, s: 0.8 }), figure({ robe: INK.ochre, seed: 43 })],
  };
}

const SCENES = {
  intro(g, ox, t) {
    draw(g, SP.mtn, ox + 380, 1300, 0.8, 0.95);
    g.drawImage(SP.plum, ox + 120, 380);
    brushText(g, '元旦', ox - 80, 760, 260, prog(t, cue('intro.title') - 0.05, 0.9));
    stamp(g, '一月一日', ox + 250, 800, t - cue('intro.seal'), { size: 150 });
    splash(g, ox + 250, 800, t - cue('intro.seal'), { color: INK.red, rad: 120, seed: 3 });
    stamp(g, '答题', ox - 330, 990, t - cue('intro.hint'), { size: 120, rot: 0.06 });
  },
  a1(g, ox, t) {
    const ly = 920;
    const kl = easeOut(prog(t, cue('a1.line') - 0.2, 0.6));
    if (kl > 0) stroke(g, [[ox - 420, ly], [lerp(ox - 420, ox + 40, kl * 0.5), ly - 4], [lerp(ox - 420, ox + 40, kl), ly + 2]], 34, { seed: 5, dry: 5 });
    const kr = easeOut(prog(t, cue('a1.rise') - 0.9, 0.9));
    if (kr > 0) {
      g.save(); g.beginPath(); g.rect(ox - 500, 0, 700, ly - 14); g.clip();
      const sy = lerp(ly + 90, ly - 130, kr);
      blot(g, ox - 190, sy, 170, INK.red2, 0.25);
      g.fillStyle = rgba(INK.red, 0.9); g.beginPath(); g.arc(ox - 190, sy, 88, 0, Math.PI * 2); g.fill();
      g.restore();
    }
    const kz = prog(t, cue('a1.rise'), 0.6);
    brushText(g, '旦', ox + 250, 800, 300, kz);
    label(g, '日', ox - 190, 620, easeOut(prog(t, cue('a1.rise') + 0.5, 0.3)), 46);
    label(g, '地平线', ox - 330, 975, easeOut(prog(t, cue('a1.rise') + 0.7, 0.3)), 40);
    brushText(g, '元旦', ox, 1145, 160, prog(t, cue('a1.yuan') - 0.05, 0.6), { color: INK.red });
  },
  poem(g, ox, t) {
    g.drawImage(SP.plum2, ox - 560, 1040);
    const s = cue('poem.scroll');
    const k = easeOut(prog(t, s - 0.2, 0.8));
    const x0 = ox - 230, top = 380, hh = 820 * k;
    if (k > 0) {
      g.fillStyle = INK.silk; g.fillRect(x0 - 26, top, 512, hh);
      g.fillStyle = '#F8F1E2'; g.fillRect(x0, top + 30, 460, Math.max(0, hh - 60));
      stroke(g, [[x0 - 46, top], [x0 + 506, top]], 22, { seed: 2, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
      stroke(g, [[x0 - 46, top + hh], [x0 + 506, top + hh]], 22, { seed: 3, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
      g.save(); g.beginPath(); g.rect(x0, top, 460, hh); g.clip();
      brushText(g, '四气新元旦', ox + 90, 480, 100, prog(t, s + 0.4, 1.8), { vertical: true, align: 'start' });
      brushText(g, '万寿初春朝', ox - 40, 480, 100, prog(t, s + 1.4, 1.8), { vertical: true, align: 'start' });
      brushText(g, '萧子云', ox - 150, 860, 52, prog(t, s + 2.4, 0.6), { vertical: true, align: 'start', color: INK.ink2 });
      g.restore();
    }
    stamp(g, '正月初一', ox + 330, 900, t - cue('poem.lunar'), { size: 150, rot: 0.08 });
  },
  three(g, ox, t) {
    ['three.xia', 'three.shang', 'three.zhou'].forEach((n, i) => {
      const d = t - cue(n);
      if (d < -0.35) return;
      const y = d < 0 ? lerp(-640, 420, easeIn(1 + d / 0.35)) : 420 + 18 * Math.exp(-d * 8) * Math.cos(d * 22);
      const sp = SP.hang[i];
      g.save(); g.translate(ox + (i - 1) * 300, y); g.rotate(0.04 * Math.exp(-Math.max(0, d) * 3) * Math.sin(Math.max(0, d) * 9));
      g.drawImage(sp, -sp.width / 2, 0); g.restore();
    });
  },
  qin(g, ox, t) {
    const k = clamp01(prog(t, TL.shot.qin.t0 - 0.6, 1.0));
    draw(g, SP.palace, ox, 730, 1.0, k);
    draw(g, SP.emperor, ox - 40, 1250, 1.0, k);
    stamp(g, '秦', ox + 290, 980, t - cue('qin.seal'), { size: 160, rot: -0.06 });
    splash(g, ox + 290, 980, t - cue('qin.seal'), { color: INK.red, rad: 140, seed: 8 });
  },
  a2(g, ox, t) {
    const tc = cue('a2.taichu');
    const m = clamp01((t - (tc + 0.4)) / 0.5);
    g.save(); g.filter = `blur(${(5 * Math.sin(Math.PI * m)).toFixed(2)}px)`;
    if (m < 1) brushText(g, '十月', ox, 760, 280, prog(t, cue('a2.shiyue') - 0.1, 0.7), { alpha: 1 - m });
    if (m > 0) brushText(g, '正月', ox, 760, 280, 1, { alpha: m, color: INK.red });
    g.restore();
    const ku = easeOut(prog(t, tc - 0.3, 0.7));
    if (ku > 0) {
      const wd = 640 * ku, y = 1080;
      g.fillStyle = '#F8F1E2'; g.fillRect(ox - wd / 2, y - 70, wd, 140);
      g.strokeStyle = rgba(INK.ink, 0.6); g.lineWidth = 3; g.strokeRect(ox - wd / 2, y - 70, wd, 140);
      for (const sx of [-1, 1]) stroke(g, [[ox + sx * wd / 2, y - 90], [ox + sx * wd / 2, y + 90]], 20, { seed: 4 + sx, dry: 0, color: '#5A4632', taper: [0.02, 0.02] });
      g.save(); g.beginPath(); g.rect(ox - wd / 2, y - 70, wd, 140); g.clip();
      brushText(g, '太初历', ox, y, 96, prog(t, tc + 0.2, 0.6));
      g.restore();
    }
  },
  yuanri(g, ox, t) {
    draw(g, SP.door, ox - 30, 1260, 0.95, clamp01(prog(t, TL.shot.yuanri.t0 - 0.6, 1.0)));
    const sw = Math.sin(t * 3) * 0.06;
    g.save(); g.translate(ox + 380, 420); g.rotate(sw);
    g.strokeStyle = INK.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, 520); g.stroke();
    for (let i = 0; i < 12; i++) {
      const y = 40 + i * 40, sd = i % 2 ? 1 : -1;
      g.save(); g.translate(sd * 14, y); g.rotate(sd * 0.5);
      g.fillStyle = INK.red; g.fillRect(-8, -24, 16, 48); g.fillStyle = INK.gold; g.fillRect(-8, -24, 16, 6); g.restore();
    }
    g.restore();
  },
  a3(g, ox, t) {
    const c = cue('a3.cal'), f = cue('a3.flip');
    const d = t - c;
    if (d < -0.35) return;
    const y = d < 0 ? lerp(-300, 820, easeIn(1 + d / 0.35)) : 820 + 14 * Math.exp(-d * 9) * Math.cos(d * 26);
    const cx = ox - 40;
    g.drawImage(SP.calNew, cx - SP.calNew.width / 2, y - SP.calNew.height / 2);
    const kf = easeIn(prog(t, f - 0.3, 0.3));
    if (kf < 1) {
      g.save(); g.translate(cx, y - 245); g.rotate(-kf * 0.5); g.translate(kf * -120, -kf * 300); g.globalAlpha = 1 - kf;
      g.drawImage(SP.calOld, -SP.calOld.width / 2, 0); g.restore();
    }
    splash(g, cx, y, t - f, { color: INK.red, rad: 220, seed: 15 });
  },
  naming(g, ox, t) {
    const pages = [['naming.left', 'naming.left_seal', SP.calYuandan, -230, '元旦'], ['naming.right', 'naming.right_seal', SP.calChunjie, 230, '春节']];
    for (const [a, b, sp, dx, seal] of pages) {
      const k = easeOutBack(prog(t, cue(a) - 0.15, 0.4), 1.6);
      if (k <= 0) continue;
      g.save(); g.globalAlpha = clamp01(k * 2); g.translate(ox + dx, 830); g.scale(0.95 * k, 0.95 * k); g.rotate((dx < 0 ? -1 : 1) * 0.04);
      g.drawImage(sp, -sp.width / 2, -sp.height / 2); g.restore();
      stamp(g, seal, ox + dx + 120, 1030, t - cue(b), { size: 110, rot: 0.1 });
    }
  },
  a4(g, ox, t) {
    const fw = cue('a4.firework');
    firework(g, ox - 210, 560, t - fw, INK.red, 3);
    firework(g, ox + 170, 470, t - fw - 0.25, INK.gold, 7, 180);
    firework(g, ox + 330, 700, t - fw - 0.5, INK.red2, 11, 150);
    draw(g, SP.pine, ox - 380, 1270, 0.75);
    SP.fam.forEach((sp, i) => draw(g, sp, ox - 120 + i * 130, 1260, 0.9));
    brushText(g, '新年快乐', ox, 900, 130, prog(t, cue('a4.reveal') + 0.9, 0.9), { color: INK.red });
    stamp(g, '元旦', ox + 320, 1080, t - cue('a4.final'), { size: 150, rot: 0.05 });
    splash(g, ox + 320, 1080, t - cue('a4.final'), { color: INK.red, rad: 170, seed: 21 });
  },
};

function sunrise(g, cx, t) {                            // 开篇：红日从远山后升起（远景视差）
  const x0 = TL.shot.intro.x;
  const a = 1 - prog(cx - x0, 600, 1400);
  if (a <= 0) return;
  const k = easeOut(prog(t, cue('intro.sunrise'), 4.5));
  const x = W / 2 - 260 - (cx - x0) * 0.15, y = lerp(860, 540, k);
  blot(g, x, y, 200, INK.red2, 0.2 * a);
  g.fillStyle = rgba(INK.red, 0.85 * a); g.beginPath(); g.arc(x, y, 80, 0, Math.PI * 2); g.fill();
}
const FLAKES = (() => { const r = rng(77); return Array.from({ length: 150 }, () => [r(), r(), r(), r()]); })();
function snow(g, cx, t) {                               // 前景飘雪
  for (const [a, b, c, d] of FLAKES) {
    const s = 2 + d * 4.5;
    const x = ((a * 1400 - cx * (0.4 + d * 0.6) + Math.sin(t * (0.6 + c) + a * 9) * 30) % 1400 + 1400) % 1400 - 160;
    const y = ((b * H + t * (40 + d * 70)) % H);
    g.fillStyle = 'rgba(255,255,255,0.95)'; g.beginPath(); g.arc(x, y, s, 0, Math.PI * 2); g.fill();
    g.strokeStyle = 'rgba(120,110,100,0.25)'; g.lineWidth = 1; g.stroke();
  }
}

runScroll({
  scenes: SCENES, sprites: buildSprites, backdrop: sunrise, overlay: snow, fontSample: '元旦正月初一',
  shakes: [['a1.reveal', 14], ['qin.palace', 8], ['a3.flip', 8], ['a4.final', 16]],
});
