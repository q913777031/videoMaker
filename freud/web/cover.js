// 封面：鎏金椭圆画框里的版画侧面像 + 大标题 + 酒红丝带钩子。seek(0) 为 9:16，seek(1) 为 3:4（取上方 1080×1440）。
import { W, rgba } from '../../chongyang/web/ink.js';
import { C, paintOldPaper, damaskTile, goldFrame, profile, plate } from './vienna.js';

function text(g, s, x, y, { size = 80, weight = 900, color = C.ink, italic = false, spacing = 0, halo = true } = {}) {
  g.save();
  g.font = `${italic ? 'italic ' : ''}${weight} ${size}px NotoSerifSC`;
  g.textAlign = 'center'; g.textBaseline = 'middle';
  if (spacing) g.letterSpacing = `${spacing}px`;
  if (halo) { g.lineJoin = 'round'; g.lineWidth = size * 0.16; g.strokeStyle = rgba(C.paper, 0.95); g.strokeText(s, x, y); }
  g.fillStyle = color; g.fillText(s, x, y);
  g.restore();
}
function ribbon(g, y, s) {                                // 酒红丝带（两端燕尾）
  const x0 = 110, x1 = W - 110, h = 64;
  g.fillStyle = '#5A1414';
  for (const [a, b, d] of [[x0 - 70, x0 + 10, -1], [x1 + 70, x1 - 10, 1]]) {
    g.beginPath(); g.moveTo(b, y - h + 14); g.lineTo(a, y - h + 14); g.lineTo(a + d * -30, y + 7); g.lineTo(a, y + h); g.lineTo(b, y + h); g.closePath(); g.fill();
  }
  g.fillStyle = C.oxblood; g.fillRect(x0, y - h, x1 - x0, h * 2);
  g.strokeStyle = rgba(C.gold2, 0.9); g.lineWidth = 3; g.strokeRect(x0 + 10, y - h + 10, x1 - x0 - 20, h * 2 - 20);
  text(g, s, W / 2, y + 2, { size: 76, color: '#F6ECD6', halo: false });
}
let TILE = null;
function draw(g, H, v) {
  const Y = y => (v ? y * 0.75 : y);
  g.setTransform(1, 0, 0, 1, 0, 0);
  const p = document.createElement('canvas'); p.width = W; p.height = 1920; paintOldPaper(p.getContext('2d'));
  g.drawImage(p, 0, 0, W, H);
  g.save(); g.globalAlpha = 0.5;
  for (let x = 0; x < W; x += 240) for (let y = 0; y < H; y += 320) g.drawImage(TILE, x, y);
  g.restore();
  const vg = g.createRadialGradient(W / 2, H * 0.4, H * 0.2, W / 2, H * 0.45, H * 0.75);
  vg.addColorStop(0, 'rgba(40,24,12,0)'); vg.addColorStop(1, 'rgba(40,24,12,0.45)');
  g.fillStyle = vg; g.fillRect(0, 0, W, H);
  text(g, '心理学名家 · 精神分析', W / 2, Y(160), { size: 38, weight: 700, color: C.ink2, spacing: 6 });
  const fy = v ? 470 : 640;
  goldFrame(g, W / 2, fy, v ? 380 : 500, v ? 480 : 640, (g) => { g.save(); g.translate(W / 2, fy - 20); g.scale(v ? 0.78 : 1, v ? 0.78 : 1); profile(g, 0, 0, 1); g.restore(); }, { oval: true });
  const ty = v ? 860 : 1150;
  text(g, '弗洛伊德', W / 2, ty, { size: v ? 150 : 170, color: C.ink, spacing: 18 });
  text(g, 'SIGMUND FREUD · 1856–1939', W / 2, ty + (v ? 105 : 120), { size: 40, weight: 700, color: C.ink2, italic: true, spacing: 4 });
  ribbon(g, ty + (v ? 210 : 260), '你没发现的那部分自己');
  const py = ty + (v ? 345 : 430);
  ['本我', '自我', '超我'].forEach((s, i) => plate(g, W / 2 + (i - 1) * 270, py, s, 1, 220));
  text(g, '90 秒看懂精神分析', W / 2, py + (v ? 95 : 110), { size: 54, weight: 900, color: C.oxblood });
}
async function boot() {
  for (const f of ['900 80px NotoSerifSC', '700 40px NotoSerifSC']) await document.fonts.load(f, '弗洛伊德你没发现的那部分自己本我超我精神分析心理学名家');
  TILE = damaskTile();
  window.AC.ready = true;
}
const g = document.getElementById('c').getContext('2d');
window.AC = {
  ready: false,
  seek(t) { g.clearRect(0, 0, W, 1920); const v = Math.round(t); draw(g, v ? 1440 : 1920, v); return v; },
  info() { return { shots: 2, end: 2 }; },
};
boot().catch(e => { window.AC.error = String(e && e.stack || e); console.error(e); });
