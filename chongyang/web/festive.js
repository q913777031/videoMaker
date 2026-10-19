// 节庆小景（水墨笔触）：红梅、木门与春联、鞭炮串、水墨烟花、日历页、红灯笼、红包、铜钱串、年兽、篝火、年夜饭桌。
// 与 ink.js 一样都是确定性绘制：随机数只来自 seed。
import { INK, clamp01, lerp, easeOut, rng, canvas, rgba, stroke, curve, blot } from './ink.js';

export function sprite(w, h, f) { const c = canvas(w, h); f(c.getContext('2d'), w, h); return c; }

/** 红梅一枝（原点：枝根，向右下伸出）。 */
export function plum(seed = 3) {
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

/** 木门（原点：底部中心）。couplets=[右联, 左联] 为 null 时不贴春联；fu 为是否贴倒“福”。 */
export function door({ couplets = ['爆竹声中一岁除', '春风送暖入屠苏'], fu = true, upside = false } = {}) {
  return sprite(760, 760, (g, w, h) => {
    const cx = w / 2, b = h - 10;
    g.fillStyle = '#7A4A30'; g.fillRect(cx - 200, b - 600, 400, 600);
    g.strokeStyle = rgba(INK.ink, 0.85); g.lineWidth = 5; g.strokeRect(cx - 200, b - 600, 400, 600);
    g.beginPath(); g.moveTo(cx, b - 600); g.lineTo(cx, b); g.stroke();
    for (const x of [-100, 100]) for (const y of [-470, -250]) { g.strokeStyle = 'rgba(40,24,16,0.6)'; g.lineWidth = 3; g.strokeRect(cx + x - 70, b + y - 80, 140, 160); }
    for (const x of [-26, 26]) { g.fillStyle = '#C8A15E'; g.beginPath(); g.arc(cx + x, b - 300, 14, 0, Math.PI * 2); g.fill(); }
    stroke(g, [[cx - 250, b - 610], [cx + 250, b - 610]], 30, { seed: 3, dry: 2, color: INK.ink, taper: [0.02, 0.02] });
    if (couplets) {
      const couplet = (x, text) => {
        g.fillStyle = INK.red; g.fillRect(x - 40, b - 590, 80, 560);
        g.fillStyle = '#1E1B19'; g.font = '62px MaShanZheng'; g.textAlign = 'center'; g.textBaseline = 'middle';
        const step = Math.min(78, 540 / text.length), y0 = b - 590 + (560 - step * text.length) / 2;
        [...text].forEach((ch, i) => g.fillText(ch, x, y0 + step * (i + 0.5)));
      };
      couplet(cx + 260, couplets[0]);
      couplet(cx - 260, couplets[1]);
    }
    if (fu) {
      g.fillStyle = INK.red; g.save(); g.translate(cx, b - 400); g.rotate(Math.PI / 4); g.fillRect(-70, -70, 140, 140); g.restore();
      g.save(); g.translate(cx, b - 396); if (upside) g.rotate(Math.PI);
      g.fillStyle = '#1E1B19'; g.font = '110px MaShanZheng'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('福', 0, upside ? -8 : 0);
      g.restore();
    }
  });
}

/** 鞭炮串：在 (x,y) 起垂下 n 节，随 t 轻摆。 */
export function firecrackers(g, x, y, t, n = 12, s = 1) {
  g.save(); g.translate(x, y); g.rotate(Math.sin(t * 3) * 0.06); g.scale(s, s);
  g.strokeStyle = INK.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, 40 + n * 40); g.stroke();
  for (let i = 0; i < n; i++) {
    const yy = 40 + i * 40, sd = i % 2 ? 1 : -1;
    g.save(); g.translate(sd * 14, yy); g.rotate(sd * 0.5);
    g.fillStyle = INK.red; g.fillRect(-8, -24, 16, 48); g.fillStyle = INK.gold; g.fillRect(-8, -24, 16, 6); g.restore();
  }
  g.restore();
}

/** 水墨烟花：dt 秒后绽开并散落。 */
export function firework(g, x, y, dt, color, seed, R = 210) {
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

/** 手撕日历一页（原点：中心）。 */
export function calPage(top, big, bottom, { red = true, w = 380, h = 470 } = {}) {
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

/** 红灯笼（原点：挂绳顶端；lit 为点亮程度 0–1）。 */
export function lantern(g, x, y, s = 1, lit = 1, t = 0, seed = 1) {
  g.save(); g.translate(x, y); g.rotate(Math.sin(t * 2 + seed) * 0.05); g.scale(s, s);
  g.strokeStyle = INK.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, 60); g.stroke();
  if (lit > 0) blot(g, 0, 160, 170, '#FF9A3C', 0.35 * lit);
  g.fillStyle = '#2A2622'; g.fillRect(-34, 56, 68, 18); g.fillRect(-34, 246, 68, 18);
  const grd = g.createRadialGradient(-20, 140, 10, 0, 160, 110);
  grd.addColorStop(0, lit > 0 ? '#F25A3A' : INK.red); grd.addColorStop(1, '#9E2A20');
  g.fillStyle = grd; g.beginPath(); g.ellipse(0, 160, 96, 92, 0, 0, Math.PI * 2); g.fill();
  g.strokeStyle = rgba('#5A1A12', 0.6); g.lineWidth = 2;
  for (const k of [-0.6, -0.3, 0, 0.3, 0.6]) { g.beginPath(); g.ellipse(0, 160, 96 * Math.abs(k) + 2, 92, 0, 0, Math.PI * 2); g.stroke(); }
  g.strokeStyle = INK.gold; g.lineWidth = 3;
  for (let i = -3; i <= 3; i++) { g.beginPath(); g.moveTo(i * 5, 264); g.lineTo(i * 6, 330); g.stroke(); }
  g.restore();
}

/** 红包（原点：中心）。 */
export function redEnvelope(g, x, y, s = 1, rot = 0) {
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  g.fillStyle = INK.red; g.beginPath(); g.roundRect(-60, -85, 120, 170, 10); g.fill();
  g.fillStyle = '#A82E24'; g.beginPath(); g.moveTo(-60, -85); g.lineTo(0, -30); g.lineTo(60, -85); g.closePath(); g.fill();
  g.fillStyle = INK.gold; g.beginPath(); g.arc(0, -30, 18, 0, Math.PI * 2); g.fill();
  g.fillStyle = INK.gold; g.font = '64px MaShanZheng'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('福', 0, 34);
  g.restore();
}

/** 铜钱串（原点：顶端）。 */
export function coinString(g, x, y, t, n = 7) {
  g.save(); g.translate(x, y); g.rotate(Math.sin(t * 2.5) * 0.08);
  g.strokeStyle = INK.red; g.lineWidth = 4; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, n * 40 + 20); g.stroke();
  for (let i = 0; i < n; i++) {
    const cy = 30 + i * 40;
    g.fillStyle = '#C8A15E'; g.beginPath(); g.arc(0, cy, 22, 0, Math.PI * 2); g.fill();
    g.strokeStyle = rgba(INK.ink, 0.7); g.lineWidth = 2; g.stroke();
    g.fillStyle = INK.paper; g.fillRect(-6, cy - 6, 12, 12);
  }
  g.restore();
}

/** 年兽（原点：脚底中心，面朝左）：浓墨身形、独角、红眼、长尾。 */
export function nianBeast(seed = 5) {
  return sprite(720, 520, (g, w, h) => {
    const r = rng(seed);
    g.filter = 'blur(3px)';
    for (let i = 0; i < 26; i++) blot(g, w * (0.3 + r() * 0.45), h * (0.42 + r() * 0.3), 70 + r() * 60, '#1E1B19', 0.45);
    g.filter = 'none';
    g.fillStyle = rgba('#1E1B19', 0.92);
    g.beginPath(); g.ellipse(w * 0.5, h * 0.55, 220, 120, -0.05, 0, Math.PI * 2); g.fill();
    g.beginPath(); g.ellipse(w * 0.22, h * 0.42, 110, 95, 0.2, 0, Math.PI * 2); g.fill();
    for (const x of [0.32, 0.45, 0.6, 0.72]) stroke(g, [[w * x, h * 0.62], [w * x - 6, h * 0.82], [w * x - 14, h - 8]], 34, { seed: seed + x * 10, dry: 2, taper: [0.05, 0.05] });
    stroke(g, curve([[w * 0.2, h * 0.28], [w * 0.16, h * 0.12], [w * 0.24, h * 0.02]], 5), 22, { seed: seed + 3, dry: 1, taper: [0.02, 0.8] });
    stroke(g, curve([[w * 0.72, h * 0.48], [w * 0.88, h * 0.35], [w * 0.96, h * 0.12], [w * 0.88, h * 0.04]], 6), 20, { seed: seed + 4, dry: 3, taper: [0.05, 0.9] });
    for (let i = 0; i < 14; i++) stroke(g, [[w * (0.3 + i * 0.03), h * 0.36], [w * (0.31 + i * 0.03), h * 0.26 - r() * 20]], 8, { seed: seed + 20 + i, dry: 0, taper: [0.05, 0.8] });
    g.fillStyle = '#E8392A'; g.beginPath(); g.ellipse(w * 0.14, h * 0.38, 16, 11, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#FFE08A'; g.beginPath(); g.arc(w * 0.135, h * 0.38, 4, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#F7EFE0';
    for (let i = 0; i < 4; i++) { g.beginPath(); g.moveTo(w * (0.05 + i * 0.03), h * 0.5); g.lineTo(w * (0.065 + i * 0.03), h * 0.56); g.lineTo(w * (0.08 + i * 0.03), h * 0.5); g.fill(); }
  });
}

/** 篝火（原点：底部中心）：t 驱动火舌摆动。 */
export function bonfire(g, x, y, t, s = 1, seed = 2) {
  g.save(); g.translate(x, y); g.scale(s, s);
  for (const [a, l] of [[-0.5, 150], [0.5, 150], [-0.15, 160], [0.2, 140]]) {
    g.save(); g.rotate(a); stroke(g, [[-l / 2, 0], [0, -6], [l / 2, 0]], 26, { seed: seed + l, dry: 2, color: '#4A3A2E', taper: [0.02, 0.02] }); g.restore();
  }
  blot(g, 0, -90, 190, '#FF9A3C', 0.35);
  const r = rng(seed);
  for (let i = 0; i < 9; i++) {
    const ph = r() * 6, hgt = 120 + r() * 120, xx = (r() - 0.5) * 110;
    const sw = Math.sin(t * (5 + r() * 3) + ph) * 18;
    const col = i % 3 === 0 ? '#F2C14E' : i % 3 === 1 ? '#E8603A' : INK.red;
    g.fillStyle = rgba(col, 0.75);
    g.beginPath(); g.moveTo(xx - 34, -10); g.quadraticCurveTo(xx - 30 + sw, -hgt * 0.6, xx + sw * 1.6, -hgt);
    g.quadraticCurveTo(xx + 30 + sw, -hgt * 0.5, xx + 34, -10); g.closePath(); g.fill();
  }
  g.restore();
}

/** 年夜饭圆桌（原点：桌面中心）。 */
export function dinnerTable() {
  return sprite(760, 360, (g, w, h) => {
    const cx = w / 2, cy = 120;
    g.fillStyle = '#7A4A30'; g.fillRect(cx - 18, cy + 40, 36, 200);
    g.fillStyle = '#9E6A45'; g.beginPath(); g.ellipse(cx, cy + 20, 340, 90, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#B98A5E'; g.beginPath(); g.ellipse(cx, cy, 340, 90, 0, 0, Math.PI * 2); g.fill();
    g.strokeStyle = rgba(INK.ink, 0.8); g.lineWidth = 4; g.stroke();
    const dish = (x, y, rw, fill) => {
      g.fillStyle = '#F7F2E8'; g.beginPath(); g.ellipse(x, y, rw, rw * 0.35, 0, 0, Math.PI * 2); g.fill();
      g.strokeStyle = rgba(INK.azure, 0.8); g.lineWidth = 3; g.stroke(); fill(x, y, rw);
    };
    dish(cx, cy - 5, 120, (x, y) => {                       // 鱼：年年有余
      g.fillStyle = '#D9803F'; g.beginPath(); g.ellipse(x - 10, y, 80, 24, 0, 0, Math.PI * 2); g.fill();
      g.beginPath(); g.moveTo(x + 62, y); g.lineTo(x + 100, y - 22); g.lineTo(x + 100, y + 22); g.closePath(); g.fill();
      g.fillStyle = INK.ink; g.beginPath(); g.arc(x - 70, y - 4, 4, 0, Math.PI * 2); g.fill();
    });
    dish(cx - 210, cy + 20, 80, (x, y) => {                 // 饺子
      for (const [dx, dy] of [[-28, -4], [0, 6], [28, -4], [-12, -14], [14, -14]]) {
        g.fillStyle = '#FBF6EC'; g.strokeStyle = rgba(INK.ink, 0.6); g.lineWidth = 2;
        g.beginPath(); g.ellipse(x + dx, y + dy, 20, 12, 0, Math.PI, 0); g.closePath(); g.fill(); g.stroke();
      }
    });
    dish(cx + 210, cy + 20, 80, (x, y) => {                 // 年糕
      g.fillStyle = '#EAD7AE'; g.fillRect(x - 40, y - 20, 80, 26); g.fillStyle = INK.red; g.beginPath(); g.arc(x, y - 22, 8, 0, Math.PI * 2); g.fill();
    });
  });
}
