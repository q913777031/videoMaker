// 《弗洛伊德：你没发现的那部分自己》：维也纳旧宅墙面上一排金色画框，镜头沿墙连续平移逐幅讲解。
// 画面为复古铜版画风：做旧纸色、深色墨线、排线阴影、鎏金画框、大马士革墙纸；镜头、字幕复用 chongyang/web/scroll.js。
import {
  W, H, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, rng, canvas, rgba, stroke, curve, blot, splash,
} from '../../chongyang/web/ink.js';
import { TL, cue, runScroll } from '../../chongyang/web/scroll.js';

const C = {
  paper: '#ECE2CC', canvas: '#EFE6D2', ink: '#2B1D14', ink2: '#5C4632', sepia: '#7A5C40', oxblood: '#7A1F1F',
  teal: '#2E5552', gold: '#B8924A', gold2: '#E3C77E', goldDark: '#7A5A26', wall: '#D8C9A8', wall2: '#C9B78F', wood: '#4A3222',
};

// ---------------------------------------------------------------- 纸、墙、画框
function paintOldPaper(g) {
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
let DAMASK = null;
function damaskTile() {                                   // 大马士革纹墙纸单元（240×320）
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
function wall(g, cx) {
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
function goldFrame(g, x, y, w, h, draw, { oval = false, k = 1 } = {}) {
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
function hatch(g, x0, y0, x1, y1, { gap = 9, angle = -0.8, color = C.ink, a = 0.35, lw = 1.3 } = {}) {
  g.save(); g.strokeStyle = rgba(color, a); g.lineWidth = lw;
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, R = Math.hypot(x1 - x0, y1 - y0) / 2;
  g.translate(cx, cy); g.rotate(angle); g.beginPath();
  for (let d = -R; d <= R; d += gap) { g.moveTo(-R, d); g.lineTo(R, d); }
  g.stroke(); g.restore();
}
function plate(g, x, y, text, k = 1, w = 0) {              // 铜铭牌
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
function label(g, text, x, y, a = 1, size = 40, color = C.ink, latin = '') {
  if (a <= 0) return;
  g.save(); g.globalAlpha = clamp01(a); g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = `700 ${size}px NotoSerifSC`; g.lineWidth = 8; g.strokeStyle = rgba(C.canvas, 0.85); g.strokeText(text, x, y);
  g.fillStyle = color; g.fillText(text, x, y);
  if (latin) { g.font = `italic 500 ${Math.round(size * 0.62)}px NotoSerifSC`; g.fillStyle = rgba(C.ink2, 0.9); g.fillText(latin, x, y + size * 0.85); }
  g.restore();
}
const P = (t, n, d = 0.5, e = easeOut) => e(prog(t, cue(n), d));
const FX = 760, FY = 790, FW = 760, FH = 820;              // 主画框尺寸（画心）

// ---------------------------------------------------------------- 各幅画
function door(g, x, y, k, light) {                        // 木门（k 为打开程度），门后透光
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
function profile(g, x, y, k) {                            // 版画风侧面像：圆眼镜、胡须、西装领
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
function horseRider(g, x, y, t, rein) {                   // 扬蹄黑马与骑手（剪影 + 排线）
  const rear = 0.25 - 0.12 * rein + Math.sin(t * 2) * 0.02;
  g.save(); g.translate(x, y + 200); g.rotate(-rear);
  g.fillStyle = '#21160F';
  g.beginPath(); g.ellipse(0, -170, 210, 90, 0, 0, Math.PI * 2); g.fill();
  g.beginPath(); g.moveTo(150, -220); g.quadraticCurveTo(220, -330, 260, -400); g.lineTo(330, -380); g.lineTo(320, -340);
  g.quadraticCurveTo(280, -300, 230, -170); g.closePath(); g.fill();
  g.beginPath(); g.ellipse(310, -385, 60, 30, 0.5, 0, Math.PI * 2); g.fill();
  for (const [lx, ang] of [[-150, 0.15], [-110, -0.1], [120, -0.9], [160, -1.2]]) { g.save(); g.translate(lx, -120); g.rotate(ang); g.fillRect(-14, 0, 28, 170); g.restore(); }
  stroke(g, curve([[-200, -190], [-280, -150], [-310, -60]], 5), 26, { color: '#21160F', seed: 4, dry: 4, taper: [0.1, 0.9] });
  for (let i = 0; i < 8; i++) stroke(g, [[200 + i * 10, -300 + i * 8], [175 + i * 10, -250 + i * 8]], 5, { color: '#21160F', seed: 10 + i, dry: 0 });
  g.fillStyle = C.oxblood; g.beginPath(); g.ellipse(-10, -280, 46, 70, -0.2, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#E8DCC6'; g.beginPath(); g.arc(-20, -370, 30, 0, Math.PI * 2); g.fill(); g.strokeStyle = C.ink; g.lineWidth = 3; g.stroke();
  g.fillStyle = C.ink; g.fillRect(-56, -404, 72, 14); g.fillRect(-42, -440, 44, 40);
  g.strokeStyle = C.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(20, -290); g.quadraticCurveTo(200, -330 + rein * 30, 300, -380); g.stroke();
  g.restore();
}
function iceberg(g, x, y, kd, kl, t) {
  const sea = y - 170;
  g.fillStyle = 'rgba(200,214,214,0.6)'; g.fillRect(x - FW / 2, y - FH / 2, FW, sea - (y - FH / 2));
  const wg = g.createLinearGradient(0, sea, 0, y + FH / 2);
  wg.addColorStop(0, 'rgba(60,90,96,0.55)'); wg.addColorStop(1, 'rgba(22,40,46,0.9)');
  g.fillStyle = wg; g.fillRect(x - FW / 2, sea, FW, y + FH / 2 - sea);
  g.fillStyle = '#F4F1EA'; g.beginPath(); g.moveTo(x - 90, sea); g.lineTo(x - 30, sea - 140); g.lineTo(x + 10, sea - 110); g.lineTo(x + 60, sea - 170); g.lineTo(x + 110, sea); g.closePath(); g.fill();
  g.strokeStyle = C.ink; g.lineWidth = 3; g.stroke();
  if (kd > 0) {
    g.save(); g.beginPath(); g.rect(x - FW / 2, sea, FW, (y + FH / 2 - sea) * kd); g.clip();
    g.fillStyle = 'rgba(214,226,228,0.85)'; g.beginPath(); g.moveTo(x - 90, sea); g.lineTo(x - 260, sea + 220); g.lineTo(x - 300, sea + 470); g.lineTo(x - 120, sea + 560);
    g.lineTo(x + 180, sea + 540); g.lineTo(x + 300, sea + 330); g.lineTo(x + 200, sea + 120); g.lineTo(x + 110, sea); g.closePath(); g.fill();
    g.strokeStyle = rgba(C.ink, 0.7); g.lineWidth = 3; g.stroke();
    g.save(); g.clip(); hatch(g, x - 300, sea, x + 300, sea + 560, { gap: 10, a: 0.18, color: C.teal }); g.restore();
    g.restore();
  }
  g.strokeStyle = rgba(C.ink, 0.8); g.lineWidth = 3; g.beginPath();
  for (let xx = x - FW / 2; xx <= x + FW / 2; xx += 12) { const yy = sea + Math.sin(xx * 0.05 + t * 2) * 3; xx === x - FW / 2 ? g.moveTo(xx, yy) : g.lineTo(xx, yy); }
  g.stroke();
  label(g, '意识', x + 250, sea - 110, kl, 40, C.ink, 'Conscious');
  label(g, '前意识', x - 250, sea + 60, clamp01(kl * 2 - 0.4), 36, C.ink, 'Preconscious');
  label(g, '无意识', x + 30, sea + 400, clamp01(kl * 2 - 0.8), 50, C.oxblood, 'Unconscious');
}

const SCENES = {
  intro(g, ox, t) {
    const k = easeInOut(prog(t, cue('intro.door') + 0.6, 4.5));
    goldFrame(g, ox, FY, 560, FH, (g) => {
      door(g, ox, FY + 40, k, easeOut(prog(t, cue('intro.glow') - 0.4, 1.0)));
      plate(g, ox, FY - 330, 'Berggasse 19', 1, 300);
    });
  },
  who(g, ox, t) {
    goldFrame(g, ox, FY - 40, 560, 720, (g) => profile(g, ox, FY - 60, prog(t, cue('who.portrait') - 0.2, 1.2)), { oval: true });
    plate(g, ox, FY + 400, 'SIGMUND FREUD  1856–1939', easeOut(prog(t, cue('who.plate') - 0.1, 0.3)), 520);
  },
  iceberg(g, ox, t) {
    goldFrame(g, ox, FY, FW, FH, (g) => iceberg(g, ox, FY, easeInOut(prog(t, cue('iceberg.deep') - 0.4, 1.4)), prog(t, cue('iceberg.labels'), 1.2), t));
  },
  trio(g, ox, t) {
    const pull = cue('trio.pull'), pk = prog(t, pull, 0.4), sw = pk > 0 ? Math.sin((t - pull) * 6) * 10 * (1 - prog(t, pull + 2, 1)) : 0;
    const panes = [['trio.id', -330, '本我', 'Id'], ['trio.ego', 0, '自我', 'Ego'], ['trio.superego', 330, '超我', 'Superego']];
    for (const [n, dx, zh, la] of panes) {
      const k = easeOutBack(prog(t, cue(n) - 0.15, 0.4), 1.4);
      goldFrame(g, ox + dx, FY - 40, 250, 420, (g) => {
        const cx = ox + dx, cy = FY - 60;
        if (la === 'Id') {
          blot(g, cx, cy + 40, 120, C.oxblood, 0.55);
          for (let i = 0; i < 7; i++) { const a = -Math.PI / 2 + (i - 3) * 0.3; stroke(g, [[cx, cy + 90], [cx + Math.cos(a) * 60, cy + 30 + Math.sin(a) * 60 + Math.sin(t * 6 + i) * 8], [cx + Math.cos(a) * 110, cy - 20 + Math.sin(a) * 100]], 22, { color: i % 2 ? C.oxblood : '#B5452E', seed: i, dry: 1, taper: [0.1, 0.9] }); }
          g.fillStyle = '#F2C14E'; for (const sx of [-1, 1]) { g.beginPath(); g.arc(cx + sx * 22, cy + 30, 7, 0, Math.PI * 2); g.fill(); }
        } else if (la === 'Ego') {
          g.save(); g.translate(sw, 0);
          g.fillStyle = C.teal; g.beginPath(); g.moveTo(cx - 40, cy + 150); g.lineTo(cx - 30, cy); g.lineTo(cx + 30, cy); g.lineTo(cx + 40, cy + 150); g.fill();
          g.fillStyle = '#E8DCC6'; g.beginPath(); g.arc(cx, cy - 35, 30, 0, Math.PI * 2); g.fill(); g.strokeStyle = C.ink; g.lineWidth = 3; g.stroke();
          stroke(g, [[cx - 30, cy + 10], [cx - 80 - pk * 20, cy - 10], [cx - 110 - pk * 20, cy - 30]], 12, { color: C.teal, seed: 3, dry: 0 });
          stroke(g, [[cx + 30, cy + 10], [cx + 80 + pk * 20, cy - 10], [cx + 110 + pk * 20, cy - 30]], 12, { color: C.teal, seed: 4, dry: 0 });
          g.restore();
        } else {
          g.strokeStyle = C.goldDark; g.lineWidth = 6;
          g.beginPath(); g.moveTo(cx, cy - 100); g.lineTo(cx, cy + 120); g.moveTo(cx - 90, cy - 70); g.lineTo(cx + 90, cy - 70); g.stroke();
          for (const sx of [-1, 1]) { g.beginPath(); g.moveTo(cx + sx * 90, cy - 70); g.lineTo(cx + sx * 90, cy - 10); g.stroke(); g.fillStyle = C.gold; g.beginPath(); g.ellipse(cx + sx * 90, cy - 6, 44, 12, 0, 0, Math.PI); g.fill(); }
          g.fillStyle = '#5A3A24'; g.fillRect(cx - 70, cy + 120, 140, 26);
          g.save(); g.translate(cx + 40, cy + 70); g.rotate(-0.5); g.fillRect(-50, -14, 70, 28); g.fillRect(-10, 0, 10, 70); g.restore();
        }
        hatch(g, cx - 125, cy - 210, cx + 125, cy + 210, { gap: 12, a: 0.08 });
      }, { k });
      label(g, zh, ox + dx, FY + 230, clamp01(k), 46, C.ink, la);
    }
    if (pk > 0) {
      for (const sx of [-1, 1]) {
        g.strokeStyle = rgba(C.oxblood, 0.8 * pk); g.lineWidth = 8; g.lineCap = 'round';
        const x0 = ox + sx * 60, x1 = ox + sx * 240;
        g.beginPath(); g.moveTo(x0, FY - 300); g.lineTo(x1, FY - 300); g.stroke();
        g.beginPath(); g.moveTo(x1, FY - 300); g.lineTo(x1 - sx * 26, FY - 318); g.moveTo(x1, FY - 300); g.lineTo(x1 - sx * 26, FY - 282); g.stroke();
      }
    }
  },
  rider(g, ox, t) {
    goldFrame(g, ox, FY, FW, FH, (g) => {
      const sky = g.createLinearGradient(0, FY - FH / 2, 0, FY + FH / 2);
      sky.addColorStop(0, '#E6DCC6'); sky.addColorStop(1, '#CDBB98');
      g.fillStyle = sky; g.fillRect(ox - FW / 2, FY - FH / 2, FW, FH);
      hatch(g, ox - FW / 2, FY + 220, ox + FW / 2, FY + FH / 2, { gap: 8, a: 0.25, angle: -0.2 });
      horseRider(g, ox - 40, FY + 110, t, easeInOut(prog(t, cue('rider.rein') - 0.2, 0.8)));
    });
    label(g, '本我 Id', ox + 230, FY + 330, P(t, 'rider.horse', 0.5), 40, C.oxblood);
    label(g, '自我 Ego', ox - 200, FY - 330, P(t, 'rider.horse', 0.5), 40, C.teal);
  },
  defense(g, ox, t) {
    goldFrame(g, ox, FY, FW, FH, (g) => {
      const fl = FY + 40;
      g.fillStyle = '#D9C9A9'; g.fillRect(ox - FW / 2, FY - FH / 2, FW, fl - (FY - FH / 2));
      g.fillStyle = '#3B2A1E'; g.fillRect(ox - FW / 2, fl, FW, FY + FH / 2 - fl);
      hatch(g, ox - FW / 2, fl, ox + FW / 2, FY + FH / 2, { gap: 7, a: 0.35, color: '#000000' });
      g.fillStyle = '#6B4A30'; g.fillRect(ox - FW / 2, fl - 14, FW, 28);
      const slam = cue('defense.slam'), ps = cue('defense.push');
      const push = easeInOut(prog(t, ps - 0.2, slam - ps - 0.2));
      const fall = easeIn(prog(t, slam - 0.45, 0.4));
      const bx = lerp(ox - 120, ox + 140, push), by = lerp(fl - 60, fl + 220, fall);
      const rat = t > cue('defense.rattle') ? Math.sin(t * 30) * 6 * Math.exp(-(t - cue('defense.rattle')) * 0.8) : 0;
      g.fillStyle = '#A07A4E'; g.fillRect(bx - 60 + rat, by - 60, 120, 120); g.strokeStyle = C.ink; g.lineWidth = 4; g.strokeRect(bx - 60 + rat, by - 60, 120, 120);
      g.fillStyle = C.oxblood; g.font = '900 80px NotoSerifSC'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('?', bx + rat, by + 4);
      const dk = easeIn(prog(t, slam - 0.15, 0.15));
      g.save(); g.translate(ox + 80, fl - 14); g.rotate(-1.3 * (1 - dk)); g.fillStyle = '#4A3222'; g.fillRect(0, 0, 160, 28); g.restore();
      const px = lerp(ox - 250, ox - 20, push);
      g.fillStyle = C.teal; g.beginPath(); g.moveTo(px - 40, fl - 14); g.lineTo(px - 10, fl - 170); g.lineTo(px + 40, fl - 170); g.lineTo(px + 30, fl - 14); g.fill();
      g.fillStyle = '#E8DCC6'; g.beginPath(); g.arc(px + 20, fl - 200, 28, 0, Math.PI * 2); g.fill(); g.strokeStyle = C.ink; g.lineWidth = 3; g.stroke();
      stroke(g, [[px + 30, fl - 140], [px + 80, fl - 100]], 12, { color: C.teal, seed: 5, dry: 0 });
      label(g, '压抑 Repression', ox, FY - 300, P(t, 'defense.slam', 0.4), 44, C.oxblood);
      label(g, '无意识', ox - 230, FY + 300, P(t, 'defense.rattle', 0.4), 38, '#EADFC8');
    });
  },
  dream(g, ox, t) {
    goldFrame(g, ox, FY, FW, FH, (g) => {
      g.fillStyle = '#2C3440'; g.fillRect(ox - FW / 2, FY - FH / 2, FW, FH);
      g.fillStyle = '#3D4756'; g.fillRect(ox + 120, FY - 330, 200, 240);
      g.fillStyle = '#F2E6C4'; g.beginPath(); g.arc(ox + 220, FY - 220, 50, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#3D4756'; g.beginPath(); g.arc(ox + 245, FY - 235, 46, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#6B4A30'; g.fillRect(ox - 320, FY + 180, 560, 50); g.fillRect(ox - 320, FY + 80, 30, 150);
      g.fillStyle = '#D8CDB6'; g.beginPath(); g.ellipse(ox - 40, FY + 165, 270, 40, 0, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#E8DCC6'; g.beginPath(); g.arc(ox - 240, FY + 130, 34, 0, Math.PI * 2); g.fill();
      const b0 = cue('dream.bubble');
      for (let i = 0; i < 4; i++) {
        const k = easeOutBack(prog(t, b0 + i * 0.35, 0.4), 1.6);
        if (k <= 0) continue;
        const bx = ox - 200 + i * 110 + Math.sin(t + i) * 10, by = FY + 60 - i * 120, r = (24 + i * 22) * k;
        g.fillStyle = 'rgba(240,230,205,0.85)'; g.beginPath(); g.arc(bx, by, r, 0, Math.PI * 2); g.fill();
        g.strokeStyle = rgba('#F2E6C4', 0.9); g.lineWidth = 3; g.stroke();
      }
      const ks = prog(t, cue('dream.symbols') - 0.2, 0.5);
      if (ks > 0) {
        const cx = ox + 130, cy = FY - 300, a = t * 0.8;
        g.save(); g.globalAlpha = ks; g.strokeStyle = C.ink; g.lineWidth = 6;
        g.save(); g.translate(cx - 50, cy + 10); g.rotate(a); g.beginPath(); g.arc(0, 0, 16, 0, Math.PI * 2); g.moveTo(16, 0); g.lineTo(60, 0); g.lineTo(60, 14); g.moveTo(46, 0); g.lineTo(46, 12); g.stroke(); g.restore();
        g.save(); g.translate(cx + 40, cy - 20); g.rotate(-a * 0.6); g.beginPath(); g.arc(0, 0, 24, 0, Math.PI * 2); g.moveTo(0, 0); g.lineTo(0, -16); g.moveTo(0, 0); g.lineTo(12, 4); g.stroke(); g.restore();
        g.save(); g.translate(cx, cy + 60); g.rotate(a * 0.4); g.beginPath(); for (let s = 0; s < 4; s++) { g.moveTo(-36 + s * 18, 24 - s * 16); g.lineTo(-18 + s * 18, 24 - s * 16); g.lineTo(-18 + s * 18, 8 - s * 16); } g.stroke(); g.restore();
        g.restore();
      }
    });
    label(g, '梦 Traum', ox, FY + 330, P(t, 'dream.sleep', 0.6), 44, C.ink);
  },
  slip(g, ox, t) {
    goldFrame(g, ox, FY, FW, 640, (g) => {
      hatch(g, ox - FW / 2, FY - 320, ox + FW / 2, FY + 320, { gap: 14, a: 0.06 });
      const ks = easeOutBack(prog(t, cue('slip.say') - 0.1, 0.4), 1.6);
      if (ks > 0) {
        g.save(); g.translate(ox, FY - 60); g.scale(ks, ks);
        g.fillStyle = '#FBF5E8'; g.strokeStyle = C.ink; g.lineWidth = 4;
        g.beginPath(); g.roundRect(-320, -110, 640, 200, 30); g.fill(); g.stroke();
        g.beginPath(); g.moveTo(-60, 90); g.lineTo(-110, 160); g.lineTo(-10, 90); g.closePath(); g.fill();
        g.fillStyle = C.ink; g.font = '700 58px NotoSerifSC'; g.textAlign = 'center'; g.textBaseline = 'middle';
        g.fillText('我宣布会议现在', -40, -50);
        const sw = prog(t, cue('slip.swap') - 0.2, 0.4);
        g.fillText('开始', 200, -50);
        if (sw > 0) {
          stroke(g, [[150, -50], [lerp(150, 260, sw), -54]], 8, { color: C.oxblood, seed: 3, dry: 0 });
          g.globalAlpha = clamp01(sw * 2 - 0.6); g.fillStyle = C.oxblood; g.font = '900 64px NotoSerifSC'; g.fillText('结束！', 120, 40);
        }
        g.restore();
      }
      g.fillStyle = C.oxblood; g.beginPath(); g.ellipse(ox - 160, FY + 200, 110, 40, 0, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#3B1010'; g.beginPath(); g.ellipse(ox - 160, FY + 200, 70, 14, 0, 0, Math.PI * 2); g.fill();
    });
    label(g, 'Freudian slip', ox, FY + 380, P(t, 'slip.swap', 0.5), 40, C.ink2);
  },
  couch(g, ox, t) {
    goldFrame(g, ox, FY, FW, FH, (g) => {
      g.fillStyle = '#CBB89A'; g.fillRect(ox - FW / 2, FY - FH / 2, FW, FH);
      hatch(g, ox - FW / 2, FY - FH / 2, ox + FW / 2, FY + 200, { gap: 11, a: 0.1, angle: -1.2 });
      g.fillStyle = '#5A3A24'; g.fillRect(ox - FW / 2, FY + 200, FW, FH / 2 - 200);
      const k = prog(t, cue('couch.couch') - 0.3, 0.8);
      g.save(); g.globalAlpha = clamp01(k);
      g.fillStyle = C.oxblood; g.beginPath(); g.roundRect(ox - 320, FY + 40, 470, 120, 30); g.fill();
      g.beginPath(); g.moveTo(ox - 320, FY + 60); g.quadraticCurveTo(ox - 360, FY - 80, ox - 250, FY - 70); g.lineTo(ox - 240, FY + 60); g.fill();
      g.strokeStyle = C.gold; g.lineWidth = 4;
      for (let i = 0; i < 6; i++) { g.beginPath(); g.moveTo(ox - 300 + i * 75, FY + 60); g.lineTo(ox - 270 + i * 75, FY + 140); g.stroke(); }
      for (let i = 0; i < 5; i++) { g.fillStyle = i % 2 ? C.gold : C.teal; g.fillRect(ox - 300 + i * 90, FY + 150, 80, 14); }
      g.fillStyle = '#3B2A1E'; for (const x of [-300, 120]) g.fillRect(ox + x, FY + 160, 20, 50);
      g.fillStyle = '#4A5A50'; g.beginPath(); g.roundRect(ox + 190, FY - 60, 140, 220, 24); g.fill();
      g.fillStyle = '#3B2A1E'; g.fillRect(ox + 200, FY + 160, 18, 50); g.fillRect(ox + 300, FY + 160, 18, 50);
      g.fillStyle = '#F2EBDD'; g.save(); g.translate(ox + 250, FY - 90); g.rotate(-0.15); g.fillRect(-40, -26, 80, 52); g.strokeStyle = C.ink; g.lineWidth = 2; g.strokeRect(-40, -26, 80, 52); g.restore();
      g.restore();
      const w0 = cue('couch.words');
      ['我梦见……', '小时候……', '其实……'].forEach((s, i) => {
        const u = (t - w0 - i * 0.5) * 0.3;
        if (u < 0 || u > 1) return;
        g.save(); g.globalAlpha = Math.sin(Math.PI * u);
        g.fillStyle = C.ink; g.font = 'italic 700 44px NotoSerifSC'; g.textAlign = 'center';
        g.fillText(s, ox - 150 + i * 60, FY - 20 - u * 280); g.restore();
      });
    });
    label(g, '自由联想 Free association', ox, FY + 360, P(t, 'couch.couch', 0.5), 38, C.ink);
  },
  critique(g, ox, t) {
    goldFrame(g, ox, FY, FW, FH, (g) => {
      hatch(g, ox - FW / 2, FY - FH / 2, ox + FW / 2, FY + FH / 2, { gap: 14, a: 0.06 });
      const sc = cue('critique.scale'), sw = cue('critique.swing');
      const drop = easeOutBack(prog(t, sc - 0.3, 0.5), 1.4);
      const tilt = t < sw ? 0.32 : 0.32 * Math.exp(-(t - sw) * 1.4) * Math.cos((t - sw) * 5);
      g.save(); g.translate(ox, FY - 200 + (1 - drop) * -300); g.globalAlpha = clamp01(drop * 2);
      g.strokeStyle = C.goldDark; g.lineWidth = 10; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, 440); g.stroke();
      g.fillStyle = C.goldDark; g.fillRect(-110, 430, 220, 30);
      g.save(); g.rotate(tilt);
      g.lineWidth = 8; g.beginPath(); g.moveTo(-260, 0); g.lineTo(260, 0); g.stroke();
      for (const sx of [-1, 1]) {
        g.lineWidth = 3; g.beginPath(); g.moveTo(sx * 260, 0); g.lineTo(sx * 200, 140); g.moveTo(sx * 260, 0); g.lineTo(sx * 320, 140); g.stroke();
        g.fillStyle = C.gold; g.beginPath(); g.ellipse(sx * 260, 140, 90, 22, 0, 0, Math.PI); g.fill();
      }
      g.save(); g.translate(-260, 120); g.rotate(-tilt);
      g.fillStyle = C.oxblood; g.fillRect(-60, -70, 120, 70); g.fillStyle = '#F2EBDD'; g.fillRect(-60, -64, 120, 8);
      g.fillStyle = C.gold2; g.font = '700 22px NotoSerifSC'; g.textAlign = 'center'; g.fillText('精神分析', 0, -26); g.restore();
      g.save(); g.translate(260, 120); g.rotate(-tilt);
      g.strokeStyle = C.ink; g.lineWidth = 6; g.beginPath(); g.arc(-20, -60, 30, 0, Math.PI * 2); g.moveTo(2, -40); g.lineTo(30, -10); g.stroke();
      g.fillStyle = 'rgba(120,160,150,0.6)'; g.beginPath(); g.moveTo(40, -90); g.lineTo(60, -90); g.lineTo(80, -10); g.lineTo(20, -10); g.closePath(); g.fill(); g.stroke();
      g.restore();
      g.restore(); g.restore();
    });
    label(g, '可证伪？ Falsifiable?', ox, FY + 360, P(t, 'critique.scale', 0.5), 40, C.oxblood);
  },
  legacy(g, ox, t) {
    ['无意识', '压抑', '防御', '自我'].forEach((s, i) => {
      const k = easeOutBack(prog(t, cue('legacy.plates') + i * 0.35, 0.35), 1.6);
      if (k <= 0) return;
      g.save(); g.translate(ox, 520 + i * 170); g.scale(k, k); plate(g, 0, 0, s, 1, 360); g.restore();
    });
  },
  end(g, ox, t) {
    const k = 1 - easeInOut(prog(t, cue('end.close'), 2.4));
    goldFrame(g, ox, FY, 560, FH, (g) => door(g, ox, FY + 40, k * 0.9, k));
    plate(g, ox, FY + 480, '认识你自己 · Know Thyself', easeOut(prog(t, cue('end.final') - 0.3, 0.3)), 560);
    splash(g, ox, FY + 480, t - cue('end.final'), { color: C.gold, rad: 200, seed: 9, n: 14 });
  },
};

runScroll({
  scenes: SCENES, sprites: () => { DAMASK = damaskTile(); }, ground: (g, cx) => wall(g, cx), paper: paintOldPaper,
  veil: 'rgba(236,226,204,', fontSample: '弗洛伊德本我自我超我无意识压抑',
  theme: {
    headFont: '500 30px NotoSerifSC', titleFont: '900 64px NotoSerifSC', capFont: '700 60px NotoSerifSC', letterSpacing: '6px',
    ink: C.ink, ink2: C.ink2, accent: C.oxblood, halo: 'rgba(239,228,206,1)', tagBg: 'rgba(239,228,206,0.9)',
    tagFont: 'italic 700 28px NotoSerifSC', tagRadius: '4px',
  },
  shakes: [['iceberg.sea', 10], ['defense.slam', 12], ['end.final', 12]],
});
