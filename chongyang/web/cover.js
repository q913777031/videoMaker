// 封面：复用水墨笔触库。seek(0) 画 9:16 竖版（1080×1920），seek(1) 画 3:4 版（取画布上方 1080×1440）。
import {
  W, INK, rng, canvas, rgba, paintPaper, mountains, mist, warmMountains, brushText, stamp, stroke, blot, splash, curve,
  pine, chrysanthemum, zhuyu, geese,
} from './ink.js';

let SP = null;
function text(g, s, x, y, { size = 80, weight = 900, font = 'NotoSerifSC', color = INK.ink, halo = 'rgba(244,238,226,0.95)', hw = 14, align = 'center' } = {}) {
  g.save();
  g.font = `${weight} ${size}px ${font}`; g.textAlign = align; g.textBaseline = 'middle';
  if (halo) { g.lineJoin = 'round'; g.lineWidth = hw; g.strokeStyle = halo; g.strokeText(s, x, y); }
  g.fillStyle = color; g.fillText(s, x, y);
  g.restore();
}
function draw(g, H, v) {
  const s = H / 1920;                                     // 3:4 版按高度压缩纵向位置
  const Y = y => y * (v ? 1440 / 1920 : 1);
  g.setTransform(1, 0, 0, 1, 0, 0);
  const paper = canvas(W, 1920); paintPaper(paper.getContext('2d'));
  g.drawImage(paper, 0, 0, W, H);
  // 红日 + 远山 + 云雾
  blot(g, 770, Y(560), 330, INK.red2, 0.22);
  g.fillStyle = rgba(INK.red, 0.88); g.beginPath(); g.arc(770, Y(560), 150, 0, Math.PI * 2); g.fill();
  g.save(); g.translate(0, Y(0) + (v ? -120 : 140));
  mountains(g, 'far', 3000); mist(g, 900, 260, 0, 3000, 0.3, 0.8, 3);
  mountains(g, 'mid', 3000); mist(g, 1160, 300, 0, 3000, 0.55, 0.9, 7);
  g.restore();
  geese(g, 560, Y(380), 0.3, 7, 1.1);
  // 近景：左下古松、右下菊花、右上茱萸
  g.drawImage(SP.pine, -120, H - SP.pine.height * 1.25 - (v ? 40 : 160), SP.pine.width * 1.25, SP.pine.height * 1.25);
  g.drawImage(SP.chry, W - 420, H - SP.chry.height * 1.35 - (v ? 0 : 60), SP.chry.width * 1.35, SP.chry.height * 1.35);
  g.save(); g.translate(W + 30, -40); g.rotate(Math.PI * 0.85);
  g.drawImage(SP.zhuyu, -SP.zhuyu.width / 2, -SP.zhuyu.height, SP.zhuyu.width, SP.zhuyu.height); g.restore();
  // 顶部小字
  text(g, '节日里的中国 · 水墨动画', 80, Y(150), { size: 38, weight: 700, font: 'NotoSansSC', color: INK.ink2, align: 'left', hw: 10 });
  // 主标题：巨大书法“重阳”
  const ty = v ? 420 : 560;
  splash(g, 430, ty + 30, 0.12, { rad: 300, seed: 4, color: INK.ink2, n: 9 });
  g.save(); g.shadowColor = 'rgba(244,238,226,0.9)'; g.shadowBlur = 30;
  brushText(g, '重阳', 430, ty, v ? 330 : 380, 1, { gap: 1.0 });
  g.restore();
  stamp(g, '九月初九', 905, ty + 110, 1, { size: 150, rot: -0.06 });
  // 钩子：为什么叫“重阳”？（朱砂笔刷底）
  const hy = v ? 700 : 900;
  { const r = rng(12), x0 = 70, x1 = 1010, h2 = 64;          // 朱砂笔刷底：上下边缘毛糙，两端飞白
    g.fillStyle = rgba(INK.red, 0.93); g.beginPath(); g.moveTo(x0, hy - h2);
    for (let x = x0; x <= x1; x += 18) g.lineTo(x, hy - h2 + (r() - 0.5) * 12 + Math.sin(x * 0.01) * 4);
    g.lineTo(x1 + 18, hy);
    for (let x = x1; x >= x0; x -= 18) g.lineTo(x, hy + h2 + (r() - 0.5) * 12 - Math.sin(x * 0.012) * 4);
    g.lineTo(x0 - 14, hy); g.closePath(); g.fill();
    for (let k = 0; k < 7; k++) {
      const yy = hy - h2 + 10 + k * 18, sx = r() < 0.5;
      stroke(g, sx ? [[x0 - 40 - r() * 30, yy], [x0 + 20, yy]] : [[x1 - 20, yy], [x1 + 30 + r() * 40, yy]], 8, { color: INK.red, alpha: 0.7, seed: 30 + k, dry: 1 });
    } }
  text(g, '为什么叫“重阳”？', 540, hy, { size: 96, color: '#FFF6E8', halo: null });
  // 答题预告卡：A / B 选项 + 问号
  const cy = v ? 930 : 1170;
  g.save();
  g.fillStyle = 'rgba(60,40,20,0.16)'; g.filter = 'blur(12px)'; g.fillRect(150, cy - 110, 800, 240); g.filter = 'none';
  g.fillStyle = '#F8F0E0'; g.beginPath(); g.roundRect(130, cy - 125, 820, 250, 26); g.fill();
  g.strokeStyle = INK.ink; g.lineWidth = 5; g.stroke();
  g.restore();
  [['A', '太阳', 330], ['B', '阳数“九”', 640]].forEach(([k, s2, x]) => {
    g.fillStyle = INK.red; g.beginPath(); g.arc(x - 150, cy, 44, 0, Math.PI * 2); g.fill();
    text(g, k, x - 150, cy + 2, { size: 54, color: '#FFF6E8', halo: null });
    text(g, s2, x - 88, cy + 2, { size: 64, halo: null, align: 'left' });
  });
  g.save(); g.translate(930, cy + 30); g.rotate(0.18);
  text(g, '?', 0, 0, { size: 170, color: INK.red, hw: 22 }); g.restore();
  // 底部钩子：3 秒答题 · 4 道题
  const by = v ? 1185 : 1450;
  text(g, '4 道题 · 每题 3 秒', 540, by, { size: 78, hw: 18 });
  text(g, '你能答对几道？', 540, by + 112, { size: 104, color: INK.red, hw: 20 });
  stamp(g, '答题', 95, by + 30, 1, { size: 110, rot: 0.1 });
  void s;
}
async function boot() {
  for (const f of ['100px MaShanZheng', '900 80px NotoSerifSC', '700 80px NotoSerifSC', '700 30px NotoSansSC']) await document.fonts.load(f, '重阳为什么九');
  warmMountains(0, 8000);
  SP = { pine: pine(3), chry: chrysanthemum(5), zhuyu: zhuyu(7, 0.9) };
  window.AC.ready = true;
}
const g = document.getElementById('c').getContext('2d');
window.AC = {
  ready: false,
  seek(t) { g.clearRect(0, 0, W, 1920); const v = Math.round(t); draw(g, v ? 1440 : 1920, v); return v; },
  info() { return { shots: 2, end: 2 }; },
};
boot().catch(e => { window.AC.error = String(e && e.stack || e); console.error(e); });
