// 维也纳旧宅画廊风格的公共绘制：做旧纸、大马士革墙纸、鎏金画框、铜版画排线、铜铭牌、标签、木门、侧面像。
// 正片（main.js）与封面（cover.js）共用。
import { W, H, clamp01, rng, canvas, rgba, stroke, blot } from '../../chongyang/web/ink.js';

export const C = {
  paper: '#ECE2CC', canvas: '#EFE6D2', ink: '#2B1D14', ink2: '#5C4632', sepia: '#7A5C40', oxblood: '#7A1F1F',
  teal: '#2E5552', gold: '#B8924A', gold2: '#E3C77E', goldDark: '#7A5A26', wall: '#D8C9A8', wall2: '#C9B78F', wood: '#4A3222',
};

// ---------------------------------------------------------------- 纸、墙、画框
export function paintOldPaper(g) {
  g.fillStyle = C.paper; g.fillRect(0, 0, W, H);
  const r = rng(11);
  for (let i = 0; i < 2600; i++) { g.fillStyle = `rgba(110,80,50,${0.02 + r() * 0.04})`; g.fillRect(r() * W, r() * H, 1 + r() * 2, 1 + r() * 2); }
  for (let i = 0; i < 14; i++) {
    const x = r() * W, y = r() * H, rad = 120 + r() * 320;
    const grd = g.createRadialGradient(x, y, 0, x, y, rad);
    grd.addColorStop(0, `rgba(140,100,60,${0.04 + r() * 0.05})`); grd.addColorStop(1, 'rgba(140,100,60,0)');
    g.fillStyle = grd; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  const v = g.createRadialGradient(W / 2, H * 0.45, H * 0.25, W / 2, H * 0.45, H * 0.8);
  v.addColorStop(0, 'rgba(50,30,15,0)'); v.addColorStop(1, 'rgba(50,30,15,0.38)');
  g.fillStyle = v; g.fillRect(0, 0, W, H);
}
export let DAMASK = null;
export function initDamask() { DAMASK = damaskTile(); }
export function damaskTile() {                                   // 大马士革纹墙纸单元（240×320）
  const c = canvas(240, 320), g = c.getContext('2d');
  g.fillStyle = C.wall; g.fillRect(0, 0, 240, 320);
  const motif = (cx, cy, s) => {
    g.save(); g.translate(cx, cy); g.scale(s, s); g.fillStyle = rgba(C.wall2, 0.9);
    g.beginPath(); g.moveTo(0, -90);
    g.bezierCurveTo(40, -60, 60, -20, 30, 10); g.bezierCurveTo(60, 30, 50, 70, 0, 90);
    g.bezierCurveTo(-50, 70, -60, 30, -30, 10); g.bezierCurveTo(-60, -20, -40, -60, 0, -90); g.fill();
    g.fillStyle = C.wall; g.beginPath(); g.ellipse(0, 0, 14, 34, 0, 0, Math.PI * 2); g.fill();
    for (const sd of [-1, 1]) { g.fillStyle = rgba(C.wall2, 0.9); g.beginPath(); g.ellipse(sd * 46, -60, 10, 22, sd * 0.6, 0, Math.PI * 2); g.fill(); }
    g.restore();
  };
  motif(120, 80, 0.8); motif(0, 240, 0.8); motif(240, 240, 0.8);
  return c;
}
export function wall(g, cx) {
  const off = ((cx % 240) + 240) % 240;
  g.save(); g.globalAlpha = 0.55;
  for (let x = -off - 240; x < W + 240; x += 240) for (let y = 300; y < 1300; y += 320) g.drawImage(DAMASK, x, y);
  g.restore();
  g.fillStyle = rgba(C.wood, 0.9); g.fillRect(-40, 300, W + 80, 18);
  g.fillStyle = rgba(C.gold, 0.8); g.fillRect(-40, 318, W + 80, 4);
  const wg = g.createLinearGradient(0, 1260, 0, 1340);
  wg.addColorStop(0, rgba(C.wood, 0.85)); wg.addColorStop(1, rgba(C.wood, 0));
  g.fillStyle = wg; g.fillRect(-40, 1260, W + 80, 80);
}
/** 鎏金画框：(x,y) 为画心中心；oval 为椭圆框；画心底色并裁剪，draw(g) 在裁剪区内作画。 */
export function goldFrame(g, x, y, w, h, draw, { oval = false, k = 1 } = {}) {
  if (k <= 0) return;
  g.save(); g.globalAlpha = clamp01(k);
  const b = 34;
  g.fillStyle = 'rgba(30,18,8,0.35)'; g.filter = 'blur(14px)';
  if (oval) { g.beginPath(); g.ellipse(x + 12, y + 18, w / 2 + b, h / 2 + b, 0, 0, Math.PI * 2); g.fill(); } else g.fillRect(x - w / 2 - b + 12, y - h / 2 - b + 18, w + 2 * b, h + 2 * b);
  g.filter = 'none';
  const grd = g.createLinearGradient(x - w / 2, y - h / 2, x + w / 2, y + h / 2);
  grd.addColorStop(0, C.gold2); grd.addColorStop(0.35, C.gold); grd.addColorStop(0.7, C.goldDark); grd.addColorStop(1, C.gold);
  g.fillStyle = grd;
  const shape = (pad) => { g.beginPath(); if (oval) g.ellipse(x, y, w / 2 + pad, h / 2 + pad, 0, 0, Math.PI * 2); else g.rect(x - w / 2 - pad, y - h / 2 - pad, w + 2 * pad, h + 2 * pad); };
  shape(b); g.fill();
  g.strokeStyle = rgba(C.goldDark, 0.9); g.lineWidth = 3; shape(b - 6); g.stroke(); shape(10); g.stroke();
  g.strokeStyle = rgba(C.gold2, 0.8); g.lineWidth = 2; shape(b - 14); g.stroke();
  if (!oval) for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {   // 四角花饰
    g.fillStyle = C.gold2; g.beginPath(); g.arc(x + sx * (w / 2 + b / 2), y + sy * (h / 2 + b / 2), 12, 0, Math.PI * 2); g.fill();
    g.fillStyle = C.goldDark; g.beginPath(); g.arc(x + sx * (w / 2 + b / 2), y + sy * (h / 2 + b / 2), 5, 0, Math.PI * 2); g.fill();
  }
  shape(0); g.fillStyle = C.canvas; g.fill();
  g.save(); shape(0); g.clip();
  const ig = g.createRadialGradient(x, y, Math.min(w, h) * 0.2, x, y, Math.max(w, h) * 0.7);
  ig.addColorStop(0, 'rgba(90,60,30,0)'); ig.addColorStop(1, 'rgba(90,60,30,0.22)');
  draw(g);
  g.fillStyle = ig; g.fillRect(x - w, y - h, w * 2, h * 2);
  g.restore();
  g.restore();
}
/** 排线阴影：在当前裁剪路径内画一组平行细线（铜版画风）。 */
export function hatch(g, x0, y0, x1, y1, { gap = 9, angle = -0.8, color = C.ink, a = 0.35, lw = 1.3 } = {}) {
  g.save(); g.strokeStyle = rgba(color, a); g.lineWidth = lw;
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, R = Math.hypot(x1 - x0, y1 - y0) / 2;
  g.translate(cx, cy); g.rotate(angle); g.beginPath();
  for (let d = -R; d <= R; d += gap) { g.moveTo(-R, d); g.lineTo(R, d); }
  g.stroke(); g.restore();
}
export function plate(g, x, y, text, k = 1, w = 0) {              // 铜铭牌
  if (k <= 0) return;
  g.save(); g.globalAlpha = clamp01(k);
  g.font = '700 34px NotoSerifSC';
  const tw = w || g.measureText(text).width + 70;
  const grd = g.createLinearGradient(0, y - 30, 0, y + 30);
  grd.addColorStop(0, C.gold2); grd.addColorStop(1, C.goldDark);
  g.fillStyle = grd; g.beginPath(); g.roundRect(x - tw / 2, y - 30, tw, 60, 8); g.fill();
  g.strokeStyle = rgba(C.ink, 0.6); g.lineWidth = 2; g.stroke();
  g.fillStyle = C.ink; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, x, y + 2);
  g.restore();
}
export function label(g, text, x, y, a = 1, size = 40, color = C.ink, latin = '') {
  if (a <= 0) return;
  g.save(); g.globalAlpha = clamp01(a); g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = `700 ${size}px NotoSerifSC`; g.lineWidth = 8; g.strokeStyle = rgba(C.canvas, 0.85); g.strokeText(text, x, y);
  g.fillStyle = color; g.fillText(text, x, y);
  if (latin) { g.font = `italic 500 ${Math.round(size * 0.62)}px NotoSerifSC`; g.fillStyle = rgba(C.ink2, 0.9); g.fillText(latin, x, y + size * 0.85); }
  g.restore();
}
// ---------------------------------------------------------------- 各幅画
export function door(g, x, y, k, light) {                        // 木门（k 为打开程度），门后透光
  g.fillStyle = '#1C120B'; g.fillRect(x - 170, y - 300, 340, 600);
  if (light > 0) { blot(g, x, y, 260, '#F2C879', 0.5 * light); g.fillStyle = rgba('#F7DFA6', 0.5 * light); g.fillRect(x - 160, y - 290, 320 * clamp01(k * 1.2), 580); }
  const dw = 340 * (1 - 0.82 * k);
  g.fillStyle = '#5A3A24'; g.fillRect(x - 170, y - 300, dw, 600);
  g.strokeStyle = rgba(C.ink, 0.8); g.lineWidth = 3; g.strokeRect(x - 170, y - 300, dw, 600);
  if (dw > 120) {
    for (const yy of [-250, -20]) { g.strokeRect(x - 170 + dw * 0.14, y + yy, dw * 0.72, 200); }
    g.fillStyle = C.gold; g.beginPath(); g.arc(x - 170 + dw * 0.86, y + 10, 12, 0, Math.PI * 2); g.fill();
  }
  g.save(); g.beginPath(); g.rect(x - 170, y - 300, dw, 600); g.clip(); hatch(g, x - 170, y - 300, x + 170, y + 300, { gap: 7, a: 0.18 }); g.restore();
}
export function profile(g, x, y, k) {                            // 版画风侧面像：圆眼镜、胡须、西装领
  g.save(); g.globalAlpha = clamp01(k * 1.5);
  g.fillStyle = '#3A2A1E'; g.beginPath(); g.moveTo(x - 260, y + 420); g.quadraticCurveTo(x - 220, y + 170, x - 40, y + 150);
  g.quadraticCurveTo(x + 160, y + 160, x + 230, y + 420); g.fill();
  g.fillStyle = '#F2EBDD'; g.beginPath(); g.moveTo(x - 60, y + 150); g.lineTo(x + 10, y + 260); g.lineTo(x + 70, y + 150); g.fill();
  g.fillStyle = '#E8DCC6'; g.beginPath(); g.ellipse(x, y - 40, 120, 155, 0, 0, Math.PI * 2); g.fill();
  g.strokeStyle = C.ink; g.lineWidth = 4; g.stroke();
  g.save(); g.beginPath(); g.ellipse(x, y - 40, 120, 155, 0, 0, Math.PI * 2); g.clip(); hatch(g, x - 140, y - 200, x - 20, y + 120, { gap: 8, a: 0.3 }); g.restore();
  g.fillStyle = '#4A3A30'; g.beginPath(); g.moveTo(x - 110, y + 10); g.quadraticCurveTo(x - 120, y + 140, x - 10, y + 175);
  g.quadraticCurveTo(x + 100, y + 150, x + 110, y + 10); g.quadraticCurveTo(x + 40, y + 60, x, y + 40); g.quadraticCurveTo(x - 40, y + 60, x - 110, y + 10); g.fill();
  for (let i = 0; i < 18; i++) stroke(g, [[x - 90 + i * 10, y + 40], [x - 85 + i * 10, y + 150 - Math.abs(i - 9) * 6]], 2, { color: '#8E7E70', seed: i, dry: 0, alpha: 0.6 });
  g.fillStyle = '#5E5048'; g.beginPath(); g.ellipse(x, y - 160, 125, 60, 0, Math.PI, 0); g.fill();
  g.strokeStyle = C.ink; g.lineWidth = 5;
  for (const sx of [-1, 1]) { g.beginPath(); g.arc(x + sx * 48, y - 40, 34, 0, Math.PI * 2); g.stroke(); }
  g.beginPath(); g.moveTo(x - 14, y - 40); g.lineTo(x + 14, y - 40); g.stroke();
  g.fillStyle = C.ink; for (const sx of [-1, 1]) { g.beginPath(); g.arc(x + sx * 48, y - 38, 6, 0, Math.PI * 2); g.fill(); }
  stroke(g, [[x, y - 20], [x - 8, y + 30], [x + 6, y + 36]], 4, { color: C.ink, seed: 3, dry: 0 });
  g.restore();
}
