// 水墨笔触库（Canvas 2D）：宣纸底、远山长卷分块、笔画、墨点、书法逐字落笔、朱砂印，以及松、菊、茱萸、鹤、人物、亭、宫檐、村舍、乌云、糕、酒壶等小景。
// 全部确定性：随机数只来自 seed，同一参数每次画出同一幅。
export const W = 1080, H = 1920;

export const INK = {
  paper: '#F1E8D6', paper2: '#E4D6BC', ink: '#262320', ink2: '#57504A', ink3: '#8E857A', mist: 'rgba(244,238,226,',
  red: '#B8372B', red2: '#D2553F', gold: '#D9A441', gold2: '#ECC872', ochre: '#B07A45', green: '#3E5546', green2: '#6E8B74',
  azure: '#4E7387', silk: '#C9D3D2',
};

// ---------------------------------------------------------------- 数学
export const clamp01 = x => (x < 0 ? 0 : x > 1 ? 1 : x);
export const lerp = (a, b, k) => a + (b - a) * k;
export const easeOut = x => 1 - Math.pow(1 - clamp01(x), 3);
export const easeIn = x => Math.pow(clamp01(x), 3);
export const easeInOut = x => { x = clamp01(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
export const easeOutBack = (x, s = 1.7) => { x = clamp01(x) - 1; return 1 + (s + 1) * x * x * x + s * x * x; };
export const prog = (t, a, d) => (d > 0 ? clamp01((t - a) / d) : (t >= a ? 1 : 0));
export const win = (t, a, b, fi = 0.3, fo = 0.4) => (t < a || t > b ? 0 : Math.min(prog(t, a, fi), 1 - prog(t, b - fo, fo)));
export function rng(seed) {
  let s = (seed * 2654435761) >>> 0 || 1;
  return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) % 1e9) / 1e9; };
}
const hash = (i, seed) => { const x = Math.sin(i * 127.1 + seed * 311.7) * 43758.5453; return x - Math.floor(x); };
export function noise(x, seed = 0) {
  const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
  return lerp(hash(i, seed), hash(i + 1, seed), u);
}
export function canvas(w, h) {
  const c = document.createElement('canvas');
  c.width = Math.ceil(w); c.height = Math.ceil(h);
  return c;
}
export const rgba = (hex, a) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`;
};

// ---------------------------------------------------------------- 宣纸
export function paintPaper(g) {
  g.fillStyle = INK.paper;
  g.fillRect(0, 0, W, H);
  const r = rng(7);
  for (let i = 0; i < 3000; i++) {
    const x = r() * W, y = r() * H, l = 6 + r() * 26, a = r() * Math.PI;
    g.strokeStyle = `rgba(120,96,60,${0.025 + r() * 0.045})`;
    g.lineWidth = 0.6 + r() * 0.8;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
  }
  for (let i = 0; i < 16; i++) {
    const x = r() * W, y = r() * H, rad = 140 + r() * 380;
    const grd = g.createRadialGradient(x, y, 0, x, y, rad);
    grd.addColorStop(0, `rgba(150,120,80,${0.03 + r() * 0.04})`);
    grd.addColorStop(1, 'rgba(150,120,80,0)');
    g.fillStyle = grd; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  const v = g.createRadialGradient(W / 2, H * 0.45, H * 0.28, W / 2, H * 0.45, H * 0.8);
  v.addColorStop(0, 'rgba(60,40,20,0)');
  v.addColorStop(1, 'rgba(60,40,20,0.26)');
  g.fillStyle = v; g.fillRect(0, 0, W, H);
}

// ---------------------------------------------------------------- 笔画
/** 沿折线画一笔：两端收锋、边缘有毛刺，另加几道飞白。pts=[[x,y],...]，w=最粗处宽度。 */
export function stroke(g, pts, w, { color = INK.ink, alpha = 0.92, seed = 1, dry = 3, taper = [0.15, 0.35] } = {}) {
  const r = rng(seed);
  const n = pts.length;
  if (n < 2) return;
  const L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
    let nx = -(b[1] - a[1]), ny = b[0] - a[0];
    const d = Math.hypot(nx, ny) || 1; nx /= d; ny /= d;
    const u = i / (n - 1);
    const prof = Math.min(1, u / taper[0] + 0.15, (1 - u) / taper[1] + 0.05);
    const ww = w * Math.max(0.08, prof) * (0.85 + 0.3 * r()) / 2;
    L.push([pts[i][0] + nx * ww, pts[i][1] + ny * ww]);
    R.push([pts[i][0] - nx * ww, pts[i][1] - ny * ww]);
  }
  g.fillStyle = rgba(color, alpha);
  g.beginPath();
  g.moveTo(L[0][0], L[0][1]);
  for (let i = 1; i < n; i++) g.lineTo(L[i][0], L[i][1]);
  for (let i = n - 1; i >= 0; i--) g.lineTo(R[i][0], R[i][1]);
  g.closePath();
  g.fill();
  g.strokeStyle = rgba(color, alpha * 0.5);
  for (let k = 0; k < dry; k++) {                          // 飞白：沿笔路的断续细线
    const off = (r() - 0.5) * w * 0.9;
    g.lineWidth = 0.8 + r() * 1.6;
    g.beginPath();
    let on = false;
    for (let i = 0; i < n; i++) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
      let nx = -(b[1] - a[1]), ny = b[0] - a[0];
      const d = Math.hypot(nx, ny) || 1; nx /= d; ny /= d;
      const x = pts[i][0] + nx * off * 1.15, y = pts[i][1] + ny * off * 1.15;
      if (r() < 0.75) { if (!on) g.moveTo(x, y); else g.lineTo(x, y); on = true; } else on = false;
    }
    g.stroke();
  }
}
/** 由控制点生成平滑曲线采样点（二次贝塞尔串联）。 */
export function curve(ctrl, step = 10) {
  const out = [];
  for (let i = 0; i < ctrl.length - 1; i++) {
    const a = ctrl[i], b = ctrl[i + 1];
    const m0 = i === 0 ? a : [(ctrl[i - 1][0] + a[0]) / 2, (ctrl[i - 1][1] + a[1]) / 2];
    const m1 = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    const seg = Math.max(2, Math.ceil(Math.hypot(m1[0] - m0[0], m1[1] - m0[1]) / step));
    for (let k = 0; k < seg; k++) {
      const u = k / seg;
      out.push([(1 - u) * (1 - u) * m0[0] + 2 * (1 - u) * u * a[0] + u * u * m1[0], (1 - u) * (1 - u) * m0[1] + 2 * (1 - u) * u * a[1] + u * u * m1[1]]);
    }
  }
  out.push(ctrl[ctrl.length - 1]);
  return out;
}
/** 墨晕：软边圆形墨块。 */
export function blot(g, x, y, r, color = INK.ink, a = 0.5) {
  const grd = g.createRadialGradient(x, y, 0, x, y, r);
  grd.addColorStop(0, rgba(color, a));
  grd.addColorStop(0.6, rgba(color, a * 0.6));
  grd.addColorStop(1, rgba(color, 0));
  g.fillStyle = grd;
  g.fillRect(x - r, y - r, r * 2, r * 2);
}
/** 撞击墨点：dt 秒后四溅并淡去。 */
export function splash(g, x, y, dt, { rad = 160, color = INK.ink, seed = 5, dur = 0.7, n = 16 } = {}) {
  if (dt < 0 || dt > dur) return;
  const k = easeOut(dt / 0.16), a = 1 - clamp01((dt - 0.25) / (dur - 0.25));
  const r = rng(seed);
  g.fillStyle = rgba(color, 0.85 * a);
  for (let i = 0; i < n; i++) {
    const ang = r() * Math.PI * 2, d = rad * (0.45 + r() * 0.8) * k, s = (5 + r() * 15) * (1 - 0.35 * k);
    g.beginPath(); g.arc(x + Math.cos(ang) * d, y + Math.sin(ang) * d, s, 0, Math.PI * 2); g.fill();
  }
}

// ---------------------------------------------------------------- 远山长卷（分块缓存，块与块之间山脊连续）
const LAYERS = {
  far: { par: 0.22, base: 860, amp: 380, color: '#6A777B', alpha: 0.2, blur: 3, seed: 11, scale: 520 },
  mid: { par: 0.5, base: 1060, amp: 360, color: '#3E474A', alpha: 0.34, blur: 1.2, seed: 23, scale: 380 },
};
const TILE = 1024, TILE_H = 1500;
const tiles = new Map();
function ridge(L, x) {
  const s = L.scale;
  const n = 0.58 * noise(x / s, L.seed) + 0.28 * noise(x / (s * 0.42), L.seed + 1) + 0.14 * noise(x / (s * 0.14), L.seed + 2);
  return L.base - L.amp * Math.pow(n, 1.7);
}
function tile(name, i) {
  const key = name + i;
  if (tiles.has(key)) return tiles.get(key);
  const L = LAYERS[name];
  const c = canvas(TILE, TILE_H), g = c.getContext('2d');
  const x0 = i * TILE;
  g.filter = `blur(${L.blur}px)`;
  g.beginPath();
  g.moveTo(0, TILE_H);
  for (let x = -4; x <= TILE + 4; x += 4) g.lineTo(x, ridge(L, x0 + x));
  g.lineTo(TILE + 4, TILE_H);
  g.closePath();
  const grd = g.createLinearGradient(0, L.base - L.amp, 0, L.base + 420);
  grd.addColorStop(0, rgba(L.color, L.alpha * 1.1));
  grd.addColorStop(0.45, rgba(L.color, L.alpha * 0.7));
  grd.addColorStop(1, rgba(L.color, 0));
  g.fillStyle = grd;
  g.fill();
  g.filter = 'none';
  const r = rng(L.seed * 1000 + i + 77);
  for (let x = 0; x < TILE; x += 9) {                       // 皴笔：山脊下的竖向短笔
    const y = ridge(L, x0 + x);
    if (r() < 0.5) continue;
    const len = 30 + r() * 120;
    g.strokeStyle = rgba(L.color, L.alpha * (0.5 + r() * 0.6));
    g.lineWidth = 1 + r() * 2.2;
    g.beginPath(); g.moveTo(x, y + 2); g.quadraticCurveTo(x + (r() - 0.5) * 30, y + len / 2, x + (r() - 0.5) * 40, y + len); g.stroke();
  }
  g.strokeStyle = rgba(L.color, L.alpha * 1.6);         // 山脊轮廓线
  g.lineWidth = 2.2;
  g.beginPath();
  for (let x = 0; x <= TILE; x += 6) { const y = ridge(L, x0 + x) + 1; x ? g.lineTo(x, y) : g.moveTo(x, y); }
  g.stroke();
  tiles.set(key, c);
  return c;
}
/** 预先生成长卷 [x0, x1]（近景坐标）范围内两层远山的全部图块，避免渲染中途生成拖慢某一帧。 */
export function warmMountains(x0, x1) {
  for (const [name, L] of Object.entries(LAYERS)) {
    for (let i = Math.floor(x0 * L.par / TILE) - 1; i <= Math.floor((x1 * L.par + W) / TILE) + 1; i++) tile(name, i);
  }
}
/** 画一层远山：camX 为长卷镜头位置（近景坐标），按视差系数平移。 */
export function mountains(g, name, camX) {
  const L = LAYERS[name];
  const off = camX * L.par;
  const i0 = Math.floor(off / TILE), i1 = Math.floor((off + W) / TILE);
  for (let i = i0; i <= i1; i++) g.drawImage(tile(name, i), Math.round(i * TILE - off), 0);
}
/** 云雾带：横向白雾，随时间缓慢漂移。 */
export function mist(g, y, h, t, camX, par = 0.35, a = 0.7, seed = 1) {
  const r = rng(seed);
  for (let k = 0; k < 7; k++) {
    const x = ((r() * 2400 - camX * par + t * (8 + r() * 10)) % 2400 + 2400) % 2400 - 600;
    const ww = 500 + r() * 600, hh = h * (0.5 + r() * 0.6);
    const yy = y + (r() - 0.5) * h * 0.6;
    const grd = g.createRadialGradient(x, yy, 0, x, yy, ww / 2);
    grd.addColorStop(0, INK.mist + a + ')');
    grd.addColorStop(1, INK.mist + '0)');
    g.save(); g.translate(x, yy); g.scale(1, hh / ww); g.translate(-x, -yy);
    g.fillStyle = grd; g.fillRect(x - ww / 2, yy - ww / 2, ww, ww);
    g.restore();
  }
}

// ---------------------------------------------------------------- 书法与印章
/** 书法逐字落笔：k∈[0,1] 为整串进度；vertical 时竖排（自上而下）。 */
export function brushText(g, text, x, y, size, k, { color = INK.ink, vertical = false, gap = 1.05, stagger = 0.7, font = 'MaShanZheng',
  align = 'center', alpha = 1 } = {}) {
  const chars = [...text], n = chars.length;
  g.save();
  g.font = `${size}px ${font}`;
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  const total = (n - 1) * size * gap;
  for (let i = 0; i < n; i++) {
    const q = clamp01((k * (n * (1 - stagger) + stagger * n) - i * stagger) / 1.0);
    if (q <= 0) continue;
    const off = (align === 'center' ? -total / 2 : 0) + i * size * gap;
    const cx = vertical ? x : x + off, cy = vertical ? y + off : y;
    g.globalAlpha = alpha * clamp01(q * 1.8);
    g.filter = q < 1 ? `blur(${((1 - q) * 4).toFixed(2)}px)` : 'none';
    const s = 1.22 - 0.22 * easeOut(q);
    g.setTransform(s, 0, 0, s, cx, cy);
    g.shadowColor = rgba(color, 0.35);
    g.shadowBlur = 5;
    g.fillStyle = color;
    g.fillText(chars[i], 0, 0);
    g.setTransform(1, 0, 0, 1, 0, 0);
  }
  g.restore();
}
const sealCache = new Map();
/** 朱砂印（白文）：文字 1–4 个；4 字时按右上、右下、左上、左下的传统顺序排。 */
export function sealSprite(text, size = 150) {
  const key = text + size;
  if (sealCache.has(key)) return sealCache.get(key);
  const chars = [...text];
  const cols = chars.length > 2 ? 2 : 1, rows = chars.length === 1 ? 1 : 2;
  const w = cols === 1 ? size * (rows === 1 ? 1 : 0.62) : size, h = size;
  const c = canvas(w + 20, h + 20), g = c.getContext('2d');
  g.translate(10, 10);
  g.fillStyle = INK.red;
  g.beginPath(); g.roundRect(0, 0, w, h, size * 0.08); g.fill();
  g.globalCompositeOperation = 'destination-out';
  g.strokeStyle = '#000'; g.lineWidth = size * 0.03;
  g.beginPath(); g.roundRect(size * 0.05, size * 0.05, w - size * 0.1, h - size * 0.1, size * 0.05); g.stroke();
  g.fillStyle = '#000';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  const fs = (rows === 1 ? 0.7 : 0.4) * size;
  g.font = `${fs}px MaShanZheng`;
  chars.forEach((ch, i) => {
    const col = cols === 2 ? 1 - Math.floor(i / 2) : 0, row = rows === 1 ? 0 : i % 2;
    const cx = cols === 1 ? w / 2 : (col + 0.5) * w / 2, cy = rows === 1 ? h / 2 : (row + 0.5) * h / 2;
    g.fillText(ch, cx, cy + fs * 0.04);
  });
  const r = rng(text.length * 31 + size);
  for (let i = 0; i < 140; i++) { g.beginPath(); g.arc(r() * w, r() * h, r() * size * 0.012, 0, Math.PI * 2); g.fill(); }
  sealCache.set(key, c);
  return c;
}
/** 盖章：dt=0 为砸下的那一帧，0.12 秒内从 1.8 倍砸到原大并轻微回弹。 */
export function stamp(g, text, x, y, dt, { size = 150, rot = -0.08, alpha = 1 } = {}) {
  if (dt < 0) return;
  const sp = sealSprite(text, size);
  const k = clamp01(dt / 0.12);
  const s = dt < 0.12 ? lerp(1.8, 1, easeIn(k)) : 1 + 0.06 * Math.exp(-(dt - 0.12) * 12) * Math.cos((dt - 0.12) * 40);
  g.save();
  g.globalAlpha = alpha * clamp01(dt / 0.05) * 0.95;
  g.translate(x, y); g.rotate(rot); g.scale(s, s);
  g.drawImage(sp, -sp.width / 2, -sp.height / 2);
  g.restore();
}

// ---------------------------------------------------------------- 小景精灵（离屏预渲染）
function sprite(w, h, draw) { const c = canvas(w, h); draw(c.getContext('2d'), w, h); return c; }
/** 画进：精灵沿 dir 方向由淡到浓逐步显现（k∈[0,1]），像一笔笔画出来。 */
export function reveal(g, sp, x, y, k, { s = 1, dir = 'up', alpha = 1 } = {}) {
  if (k <= 0) return;
  const w = sp.width * s, h = sp.height * s;
  if (k >= 1) { g.globalAlpha = alpha; g.drawImage(sp, x - w / 2, y - h, w, h); g.globalAlpha = 1; return; }
  const tmp = revealBuf(sp.width, sp.height);
  const tg = tmp.getContext('2d');
  tg.clearRect(0, 0, sp.width, sp.height);
  tg.globalCompositeOperation = 'source-over';
  tg.drawImage(sp, 0, 0);
  tg.globalCompositeOperation = 'destination-in';
  const span = dir === 'up' ? sp.height : sp.width;
  const p = lerp(-0.25, 1.05, k) * span;
  const grd = dir === 'up' ? tg.createLinearGradient(0, sp.height - p, 0, sp.height - p + span * 0.25)
    : tg.createLinearGradient(p, 0, p - span * 0.25, 0);
  grd.addColorStop(0, 'rgba(0,0,0,0)');
  grd.addColorStop(1, 'rgba(0,0,0,1)');
  tg.fillStyle = grd;
  tg.fillRect(0, 0, sp.width, sp.height);
  g.globalAlpha = alpha * clamp01(k * 3);
  g.drawImage(tmp, x - w / 2, y - h, w, h);
  g.globalAlpha = 1;
}
let _buf = null;
function revealBuf(w, h) {
  if (!_buf || _buf.width < w || _buf.height < h) _buf = canvas(Math.max(w, _buf ? _buf.width : 0), Math.max(h, _buf ? _buf.height : 0));
  return _buf;
}

/** 古松（原点：底部中心）。 */
export function pine(seed = 3) {
  return sprite(560, 720, (g, w, h) => {
    const r = rng(seed);
    const trunk = curve([[w * 0.5, h], [w * 0.46, h * 0.78], [w * 0.56, h * 0.58], [w * 0.47, h * 0.38], [w * 0.52, h * 0.2]], 8);
    stroke(g, trunk, 46, { seed: seed + 1, dry: 6, taper: [0.02, 0.5], alpha: 0.88 });
    for (let i = 0; i < 26; i++) {                       // 树皮鳞纹
      const p = trunk[Math.floor(r() * (trunk.length - 4))];
      g.strokeStyle = rgba(INK.ink, 0.5); g.lineWidth = 1.5;
      g.beginPath(); g.arc(p[0] + (r() - 0.5) * 18, p[1], 5 + r() * 5, 0.2, Math.PI - 0.2); g.stroke();
    }
    const branches = [[[w * 0.52, h * 0.42], [w * 0.75, h * 0.36], [w * 0.95, h * 0.4]], [[w * 0.48, h * 0.55], [w * 0.28, h * 0.5], [w * 0.06, h * 0.55]],
      [[w * 0.5, h * 0.25], [w * 0.68, h * 0.17], [w * 0.84, h * 0.2]], [[w * 0.5, h * 0.3], [w * 0.33, h * 0.24], [w * 0.2, h * 0.27]]];
    const pads = [];
    branches.forEach((b, i) => {
      stroke(g, curve(b, 6), 16, { seed: seed + 10 + i, dry: 2, taper: [0.05, 0.6] });
      pads.push(b[2], b[1]);
    });
    pads.push([w * 0.52, h * 0.15]);
    for (const [px, py] of pads) {                        // 松针团：墨绿晕底 + 扇形针笔
      blot(g, px, py - 6, 70, INK.green2, 0.35);
      for (let k = 0; k < 34; k++) {
        const a = Math.PI * (1.05 + r() * 0.9), l = 34 + r() * 34;
        g.strokeStyle = rgba(INK.green, 0.65 + r() * 0.3);
        g.lineWidth = 1.6 + r();
        g.beginPath(); g.moveTo(px, py); g.lineTo(px + Math.cos(a) * l * 1.3, py + Math.sin(a) * l * 0.55); g.stroke();
      }
    }
  });
}
/** 菊花一枝（原点：底部中心）。 */
export function chrysanthemum(seed = 5, { color = INK.gold, heads = 3 } = {}) {
  return sprite(380, 520, (g, w, h) => {
    const r = rng(seed);
    const pos = [[w * 0.5, h * 0.22], [w * 0.25, h * 0.38], [w * 0.75, h * 0.42]].slice(0, heads);
    pos.forEach(([x, y], i) => {
      stroke(g, curve([[w * 0.5, h], [lerp(w * 0.5, x, 0.5) + (r() - 0.5) * 20, lerp(h, y, 0.5)], [x, y + 20]], 6), 6, { seed: seed + i, dry: 0, color: INK.green });
    });
    for (let i = 0; i < 7; i++) {                         // 叶：墨绿撇笔
      const y = h * (0.5 + r() * 0.4), x = w * 0.5 + (r() - 0.5) * 30, dir = r() < 0.5 ? -1 : 1;
      stroke(g, curve([[x, y], [x + dir * 50, y - 25], [x + dir * 95, y - 5]], 6), 26, { seed: seed + 20 + i, dry: 1, color: INK.green, alpha: 0.75 });
    }
    pos.forEach(([x, y], i) => {
      const R = i === 0 ? 74 : 56;
      for (let ring = 2; ring >= 0; ring--) {
        const n = 14 + ring * 5, len = R * (0.42 + ring * 0.28);
        for (let k = 0; k < n; k++) {
          const a = (k / n) * Math.PI * 2 + ring * 0.2 + r() * 0.1;
          g.save(); g.translate(x, y); g.rotate(a);
          g.fillStyle = rgba(ring === 0 ? INK.gold2 : color, 0.9);
          g.strokeStyle = rgba(INK.ochre, 0.7); g.lineWidth = 1.2;
          g.beginPath(); g.moveTo(0, 0); g.quadraticCurveTo(len * 0.5, -len * 0.13, len, 0); g.quadraticCurveTo(len * 0.5, len * 0.13, 0, 0);
          g.fill(); g.stroke();
          g.restore();
        }
      }
      blot(g, x, y, 12, INK.ochre, 0.9);
    });
  });
}
/** 茱萸一枝：褐墨枝干、墨绿叶、成簇朱红果（原点：底部中心）。 */
export function zhuyu(seed = 7, s = 1) {
  return sprite(420 * s, 520 * s, (g, w, h) => {
    const r = rng(seed);
    g.scale(s, s);
    const W0 = 420, H0 = 520;
    const main = curve([[W0 * 0.5, H0], [W0 * 0.46, H0 * 0.7], [W0 * 0.56, H0 * 0.45], [W0 * 0.5, H0 * 0.12]], 6);
    stroke(g, main, 12, { seed, dry: 2, color: '#4A3A2E' });
    const twigs = [];
    for (let i = 0; i < 6; i++) {
      const p = main[Math.floor(main.length * (0.2 + i * 0.12))];
      const dir = i % 2 ? 1 : -1;
      const end = [p[0] + dir * (70 + r() * 60), p[1] - 40 - r() * 50];
      stroke(g, curve([p, [lerp(p[0], end[0], 0.5), p[1] - 10], end], 5), 6, { seed: seed + i, dry: 0, color: '#4A3A2E' });
      twigs.push(end);
    }
    twigs.push(main[main.length - 1]);
    for (const [x, y] of twigs) {
      for (let k = 0; k < 3; k++) {
        const a = -Math.PI / 2 + (r() - 0.5) * 2.4;
        stroke(g, [[x, y], [x + Math.cos(a) * 30, y + Math.sin(a) * 30], [x + Math.cos(a) * 55, y + Math.sin(a) * 55]], 18,
          { seed: seed + k * 7, dry: 0, color: INK.green, alpha: 0.7 });
      }
      for (let k = 0; k < 9; k++) {                        // 果簇
        const bx = x + (r() - 0.5) * 44, by = y + 6 + (r() - 0.3) * 36, br = 6 + r() * 5;
        g.fillStyle = rgba(INK.red, 0.95); g.beginPath(); g.arc(bx, by, br, 0, Math.PI * 2); g.fill();
        g.fillStyle = 'rgba(255,230,210,0.6)'; g.beginPath(); g.arc(bx - br * 0.3, by - br * 0.3, br * 0.3, 0, Math.PI * 2); g.fill();
      }
    }
  });
}
/** 仙鹤：fly=true 为展翅飞行（原点中心），否则为立姿（原点脚底）。 */
export function crane(fly = true) {
  return sprite(420, 360, (g, w, h) => {
    g.lineCap = 'round';
    if (fly) {
      const cx = w * 0.5, cy = h * 0.5;
      for (const dir of [-1, 1]) {
        g.fillStyle = '#FBF7EE'; g.strokeStyle = rgba(INK.ink, 0.8); g.lineWidth = 2;
        g.beginPath(); g.moveTo(cx - 10, cy); g.quadraticCurveTo(cx + dir * 40, cy - 120, cx + dir * 30 - 150, cy - 150 * (dir < 0 ? 1 : 0.6));
        g.quadraticCurveTo(cx + dir * 20 - 60, cy - 40, cx + 10, cy + 10); g.fill(); g.stroke();
        g.fillStyle = INK.ink;
        g.beginPath(); g.moveTo(cx + dir * 30 - 150, cy - 150 * (dir < 0 ? 1 : 0.6)); g.lineTo(cx + dir * 20 - 115, cy - 95 * (dir < 0 ? 1 : 0.7));
        g.lineTo(cx + dir * 10 - 85, cy - 120 * (dir < 0 ? 1 : 0.6)); g.closePath(); g.fill();
      }
      g.fillStyle = '#FBF7EE'; g.strokeStyle = rgba(INK.ink, 0.85); g.lineWidth = 2.5;
      g.beginPath(); g.ellipse(cx, cy, 70, 24, -0.1, 0, Math.PI * 2); g.fill(); g.stroke();
      stroke(g, curve([[cx + 60, cy - 8], [cx + 110, cy - 20], [cx + 160, cy - 18]], 4), 9, { seed: 3, dry: 0 });
      g.fillStyle = INK.red; g.beginPath(); g.arc(cx + 166, cy - 20, 7, 0, Math.PI * 2); g.fill();
      g.strokeStyle = INK.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(cx + 170, cy - 18); g.lineTo(cx + 196, cy - 12); g.stroke();
      g.lineWidth = 2.5; g.beginPath(); g.moveTo(cx - 60, cy + 6); g.lineTo(cx - 170, cy + 26); g.moveTo(cx - 60, cy + 10); g.lineTo(cx - 168, cy + 34); g.stroke();
      g.fillStyle = INK.ink; g.beginPath(); g.ellipse(cx - 70, cy + 4, 20, 9, 0.2, 0, Math.PI * 2); g.fill();
    } else {
      const cx = w * 0.5, base = h;
      g.strokeStyle = INK.ink; g.lineWidth = 3;
      g.beginPath(); g.moveTo(cx - 6, base); g.lineTo(cx - 4, base - 120); g.moveTo(cx + 14, base); g.lineTo(cx + 8, base - 120); g.stroke();
      g.fillStyle = '#FBF7EE'; g.strokeStyle = rgba(INK.ink, 0.85); g.lineWidth = 2.5;
      g.beginPath(); g.ellipse(cx, base - 150, 66, 38, -0.25, 0, Math.PI * 2); g.fill(); g.stroke();
      g.fillStyle = INK.ink; g.beginPath(); g.moveTo(cx - 60, base - 150); g.quadraticCurveTo(cx - 100, base - 120, cx - 84, base - 100);
      g.quadraticCurveTo(cx - 40, base - 120, cx - 20, base - 130); g.closePath(); g.fill();
      stroke(g, curve([[cx + 40, base - 170], [cx + 60, base - 230], [cx + 40, base - 280], [cx + 62, base - 310]], 4), 10, { seed: 8, dry: 0 });
      g.fillStyle = INK.red; g.beginPath(); g.arc(cx + 66, base - 316, 7, 0, Math.PI * 2); g.fill();
      g.strokeStyle = INK.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(cx + 70, base - 312); g.lineTo(cx + 98, base - 302); g.stroke();
    }
  });
}
/** 人物（原点：脚底中心）：robe 袍色、beard 白须、staff 拄杖、bag 臂上茱萸囊、cup 举杯、bend 弯腰（老人）。 */
export function figure({ robe = INK.azure, s = 1, beard = false, staff = false, bag = false, cup = false, bun = true, bend = 0, seed = 1, flower = false } = {}) {
  return sprite(200 * s, 300 * s, (g, w, h) => {
    g.scale(s, s);
    const cx = 100, base = 300;
    g.save(); g.translate(cx, base); g.rotate(-bend * 0.15); g.translate(-cx, -base);
    g.fillStyle = rgba(robe, 0.55);
    g.beginPath(); g.moveTo(cx - 20, base - 170); g.quadraticCurveTo(cx - 52, base - 60, cx - 46, base - 4); g.lineTo(cx + 46, base - 4);
    g.quadraticCurveTo(cx + 52, base - 60, cx + 20, base - 170); g.closePath(); g.fill();
    stroke(g, curve([[cx - 20, base - 172], [cx - 50, base - 70], [cx - 46, base - 4]], 6), 7, { seed, dry: 1 });
    stroke(g, curve([[cx + 20, base - 172], [cx + 50, base - 70], [cx + 46, base - 4]], 6), 6, { seed: seed + 1, dry: 1 });
    stroke(g, [[cx - 46, base - 4], [cx + 46, base - 4]], 5, { seed: seed + 2, dry: 0 });
    g.fillStyle = rgba(robe, 0.75);                        // 袖
    g.beginPath(); g.moveTo(cx + 16, base - 160); g.quadraticCurveTo(cx + 62, base - 130, cx + 58, base - 92); g.lineTo(cx + 30, base - 100); g.closePath(); g.fill();
    stroke(g, curve([[cx + 16, base - 160], [cx + 62, base - 130], [cx + 58, base - 92]], 5), 5, { seed: seed + 3, dry: 0 });
    if (bag) { g.fillStyle = INK.red; g.beginPath(); g.ellipse(cx + 52, base - 112, 11, 14, 0, 0, Math.PI * 2); g.fill(); }
    if (cup) { g.fillStyle = INK.paper; g.strokeStyle = INK.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(cx + 54, base - 150); g.lineTo(cx + 76, base - 150); g.lineTo(cx + 70, base - 132); g.lineTo(cx + 60, base - 132); g.closePath(); g.fill(); g.stroke(); }
    if (flower) {
      g.strokeStyle = INK.green; g.lineWidth = 3; g.beginPath(); g.moveTo(cx + 60, base - 96); g.lineTo(cx + 84, base - 150); g.stroke();
      for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2; g.fillStyle = INK.gold; g.beginPath(); g.ellipse(cx + 84 + Math.cos(a) * 9, base - 154 + Math.sin(a) * 9, 7, 3, a, 0, Math.PI * 2); g.fill(); }
    }
    g.fillStyle = '#F3E5D2'; g.beginPath(); g.arc(cx, base - 196, 22, 0, Math.PI * 2); g.fill();
    g.strokeStyle = rgba(INK.ink, 0.8); g.lineWidth = 2.5; g.stroke();
    g.fillStyle = beard ? '#CFCAC0' : INK.ink;
    g.beginPath(); g.arc(cx, base - 202, 22, Math.PI * 1.05, Math.PI * 1.95); g.fill();
    if (bun) { g.beginPath(); g.arc(cx, base - 226, 9, 0, Math.PI * 2); g.fill(); }
    if (beard) {
      g.fillStyle = '#E8E4DC'; g.strokeStyle = rgba(INK.ink, 0.5); g.lineWidth = 1.5;
      g.beginPath(); g.moveTo(cx - 12, base - 186); g.quadraticCurveTo(cx, base - 140, cx + 12, base - 186); g.closePath(); g.fill(); g.stroke();
    }
    g.restore();
    if (staff) stroke(g, [[cx - 54, base], [cx - 50, base - 120], [cx - 46, base - 230]], 7, { seed: seed + 5, dry: 0, color: '#5A4632' });
  });
}
/** 山顶小亭（原点：底部中心）。 */
export function pavilion() {
  return sprite(300, 260, (g, w, h) => {
    const cx = w / 2;
    g.fillStyle = rgba(INK.ink, 0.9);
    g.beginPath(); g.moveTo(cx, 20); g.quadraticCurveTo(cx - 60, 80, cx - 140, 92); g.quadraticCurveTo(cx - 120, 104, cx - 100, 104);
    g.lineTo(cx + 100, 104); g.quadraticCurveTo(cx + 120, 104, cx + 140, 92); g.quadraticCurveTo(cx + 60, 80, cx, 20); g.fill();
    g.fillStyle = INK.ink; g.beginPath(); g.arc(cx, 16, 7, 0, Math.PI * 2); g.fill();
    for (const x of [-80, -28, 28, 80]) stroke(g, [[cx + x, 104], [cx + x, 230]], 8, { seed: 9 + x, dry: 0, color: INK.red, alpha: 0.85 });
    stroke(g, [[cx - 110, 236], [cx + 110, 236]], 12, { seed: 4, dry: 1 });
  });
}
/** 宫殿屋檐（原点：底部中心）。 */
export function palace() {
  return sprite(1000, 460, (g, w, h) => {
    const cx = w / 2;
    g.fillStyle = rgba(INK.ink, 0.88);
    g.beginPath(); g.moveTo(cx - 330, 60); g.lineTo(cx + 330, 60); g.quadraticCurveTo(cx + 380, 150, cx + 490, 170);
    g.quadraticCurveTo(cx + 420, 196, cx + 380, 196); g.lineTo(cx - 380, 196); g.quadraticCurveTo(cx - 420, 196, cx - 490, 170);
    g.quadraticCurveTo(cx - 380, 150, cx - 330, 60); g.fill();
    stroke(g, [[cx - 360, 56], [cx + 360, 56]], 18, { seed: 2, dry: 2 });
    g.strokeStyle = rgba(INK.paper, 0.25); g.lineWidth = 3;
    for (let x = -360; x <= 360; x += 22) { g.beginPath(); g.moveTo(cx + x * 0.92, 66); g.lineTo(cx + x * 1.04, 192); g.stroke(); }
    g.fillStyle = rgba(INK.red, 0.8); g.fillRect(cx - 340, 204, 680, 26);
    for (const x of [-300, -100, 100, 300]) { g.fillStyle = rgba(INK.red, 0.85); g.fillRect(cx + x - 14, 230, 28, h - 230); }
    const grd = g.createLinearGradient(0, 230, 0, h);
    grd.addColorStop(0, 'rgba(0,0,0,0)'); grd.addColorStop(1, INK.mist + '1)');
    g.fillStyle = grd; g.fillRect(0, 230, w, h - 230);
  });
}
/** 山下村舍（原点：底部中心）。 */
export function village() {
  return sprite(760, 260, (g, w, h) => {
    const houses = [[110, 0.8], [270, 1.05], [450, 0.9], [620, 0.75]];
    for (const [x, s] of houses) {
      const ww = 150 * s, hh = 100 * s, y = h - 10;
      g.fillStyle = '#F7F1E4'; g.fillRect(x - ww / 2, y - hh, ww, hh);
      g.strokeStyle = rgba(INK.ink, 0.7); g.lineWidth = 2; g.strokeRect(x - ww / 2, y - hh, ww, hh);
      g.fillStyle = rgba(INK.ink, 0.92);
      g.beginPath(); g.moveTo(x - ww / 2 - 18, y - hh + 4); g.quadraticCurveTo(x, y - hh - 60 * s, x + ww / 2 + 18, y - hh + 4); g.closePath(); g.fill();
      g.fillRect(x - 12 * s, y - 46 * s, 24 * s, 46 * s);
    }
    blot(g, w / 2, h - 4, 380, INK.ink3, 0.12);
  });
}
/** 浓墨乌云（原点：中心）。 */
export function darkCloud(seed = 4) {
  return sprite(900, 420, (g, w, h) => {
    const r = rng(seed);
    g.filter = 'blur(6px)';
    for (let i = 0; i < 40; i++) blot(g, w * (0.12 + r() * 0.76), h * (0.3 + r() * 0.45), 70 + r() * 90, '#1E1B19', 0.35);
    g.filter = 'none';
    for (let i = 0; i < 9; i++) {
      const x = w * (0.15 + r() * 0.7), y = h * (0.35 + r() * 0.3);
      stroke(g, curve([[x - 80, y], [x, y - 30 - r() * 20], [x + 90, y + 5]], 6), 6, { seed: seed + i, dry: 1, alpha: 0.6 });
    }
  });
}
/** 重阳糕一层（原点：底部中心）。 */
export function cakeLayer(wd = 360, seed = 1) {
  return sprite(wd + 30, 120, (g, w, h) => {
    const r = rng(seed);
    const x0 = 15, y0 = 30, hh = 70;
    g.fillStyle = '#EAD7AE'; g.fillRect(x0, y0, wd, hh);
    g.fillStyle = '#C9A06A'; g.fillRect(x0, y0, wd, 16);
    g.fillStyle = 'rgba(176,122,69,0.35)'; g.fillRect(x0, y0 + 40, wd, 10);
    for (let i = 0; i < wd / 40; i++) { g.fillStyle = INK.red; g.beginPath(); g.ellipse(x0 + 20 + i * 40 + r() * 8, y0 + 8, 8, 5, 0, 0, Math.PI * 2); g.fill(); }
    stroke(g, [[x0, y0], [x0 + wd, y0]], 4, { seed, dry: 0 });
    stroke(g, [[x0, y0 + hh], [x0 + wd, y0 + hh]], 4, { seed: seed + 1, dry: 0 });
    stroke(g, [[x0, y0], [x0, y0 + hh]], 4, { seed: seed + 2, dry: 0 });
    stroke(g, [[x0 + wd, y0], [x0 + wd, y0 + hh]], 4, { seed: seed + 3, dry: 0 });
  });
}
/** 一盘蓬饵（原点：底部中心）。 */
export function cakePlate() {
  return sprite(300, 190, (g, w, h) => {
    g.fillStyle = '#F7F2E8'; g.strokeStyle = rgba(INK.ink, 0.8); g.lineWidth = 3;
    g.beginPath(); g.ellipse(w / 2, h - 34, 130, 28, 0, 0, Math.PI * 2); g.fill(); g.stroke();
    for (const [x, y] of [[-55, -60], [55, -60], [0, -84], [0, -50]]) {
      g.fillStyle = '#E3C996'; g.beginPath(); g.ellipse(w / 2 + x, h - 20 + y, 46, 26, 0, 0, Math.PI * 2); g.fill();
      g.strokeStyle = rgba(INK.ink, 0.7); g.lineWidth = 2.5; g.stroke();
      g.fillStyle = INK.red; g.beginPath(); g.arc(w / 2 + x, h - 28 + y, 5, 0, Math.PI * 2); g.fill();
    }
  });
}
/** 菊花酒：酒壶与酒杯（原点：底部中心）。 */
export function winePot() {
  return sprite(320, 300, (g, w, h) => {
    const cx = 130, b = h - 10;
    g.fillStyle = 'rgba(176,122,69,0.4)'; g.strokeStyle = INK.ink; g.lineWidth = 4;
    g.beginPath(); g.moveTo(cx - 30, b - 210); g.lineTo(cx + 30, b - 210); g.quadraticCurveTo(cx + 26, b - 160, cx + 60, b - 120);
    g.quadraticCurveTo(cx + 92, b - 70, cx + 60, b); g.lineTo(cx - 60, b); g.quadraticCurveTo(cx - 92, b - 70, cx - 60, b - 120);
    g.quadraticCurveTo(cx - 26, b - 160, cx - 30, b - 210); g.closePath(); g.fill(); g.stroke();
    stroke(g, curve([[cx + 66, b - 90], [cx + 110, b - 120], [cx + 128, b - 160]], 4), 9, { seed: 2, dry: 0 });
    g.beginPath(); g.ellipse(cx, b - 212, 34, 8, 0, 0, Math.PI * 2); g.stroke();
    const ux = 262;
    g.fillStyle = '#F7F2E8';
    g.beginPath(); g.moveTo(ux - 40, b - 70); g.lineTo(ux + 40, b - 70); g.lineTo(ux + 24, b - 6); g.lineTo(ux - 24, b - 6); g.closePath(); g.fill(); g.stroke();
    for (let k = 0; k < 10; k++) { const a = k / 10 * Math.PI * 2; g.fillStyle = INK.gold; g.beginPath(); g.ellipse(ux + Math.cos(a) * 12, b - 72 + Math.sin(a) * 4, 7, 3, a, 0, Math.PI * 2); g.fill(); }
    blot(g, cx - 10, b - 120, 30, '#FFFFFF', 0.25);
  });
}
/** 登高山（原点：底部中心）：近景山体、蜿蜒石径；pathPoint(u) 返回山路上的点（精灵坐标）。 */
export function climbMountain() {
  const w = 900, h = 900;
  const path = curve([[160, 860], [360, 800], [250, 680], [470, 590], [390, 460], [560, 360], [520, 250]], 6);
  const sp = sprite(w, h, (g) => {
    const r = rng(31);
    g.beginPath(); g.moveTo(0, h);
    const prof = curve([[0, h], [140, 740], [300, 560], [430, 330], [520, 220], [620, 300], [760, 520], [900, 760], [900, h]], 8);
    prof.forEach(p => g.lineTo(p[0], p[1]));
    g.closePath();
    const grd = g.createLinearGradient(0, 220, 0, h);
    grd.addColorStop(0, rgba(INK.ink, 0.55)); grd.addColorStop(0.5, rgba(INK.ink2, 0.3)); grd.addColorStop(1, rgba(INK.ink2, 0.05));
    g.fillStyle = grd; g.fill();
    stroke(g, prof.slice(1, -1), 7, { seed: 40, dry: 3, alpha: 0.85, taper: [0.1, 0.1] });
    for (let i = 0; i < 60; i++) {
      const p = prof[1 + Math.floor(r() * (prof.length - 3))];
      const len = 40 + r() * 140;
      stroke(g, [[p[0] + (r() - 0.5) * 30, p[1] + 10], [p[0] + (r() - 0.5) * 60, p[1] + len * 0.5], [p[0] + (r() - 0.5) * 80, p[1] + len]], 4 + r() * 4,
        { seed: 50 + i, dry: 0, alpha: 0.4 });
    }
    g.setLineDash([10, 12]); g.strokeStyle = rgba(INK.paper, 0.9); g.lineWidth = 6;
    g.beginPath(); path.forEach((p, i) => (i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1]))); g.stroke();
    g.setLineDash([]);
  });
  const lens = [0];
  for (let i = 1; i < path.length; i++) lens.push(lens[i - 1] + Math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]));
  sp.pathPoint = (u) => {
    const d = clamp01(u) * lens[lens.length - 1];
    let i = 1; while (i < lens.length - 1 && lens[i] < d) i++;
    const k = (d - lens[i - 1]) / (lens[i] - lens[i - 1] || 1);
    return [lerp(path[i - 1][0], path[i][0], k), lerp(path[i - 1][1], path[i][1], k)];
  };
  return sp;
}
/** 雁阵：在 (x,y) 画 n 只大雁组成人字形，翅膀随 t 扇动。 */
export function geese(g, x, y, t, n = 7, s = 1) {
  g.strokeStyle = rgba(INK.ink, 0.8); g.lineWidth = 3 * s; g.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const row = Math.ceil(i / 2), side = i % 2 ? 1 : -1;
    const gx = x + row * 46 * s, gy = y + side * row * 30 * s;
    const f = Math.sin(t * 7 + i) * 9 * s;
    g.beginPath(); g.moveTo(gx - 16 * s, gy - f); g.quadraticCurveTo(gx - 6 * s, gy - 4 * s, gx, gy); g.quadraticCurveTo(gx + 6 * s, gy - 4 * s, gx + 16 * s, gy - f); g.stroke();
  }
}
/** 团扇小景：圆形绢面裁出 inner 精灵（原点：扇面中心）。 */
export function roundFan(inner, label, seed = 1) {
  return sprite(360, 470, (g, w, h) => {
    const cx = w / 2, cy = 180, R = 160;
    const grd = g.createRadialGradient(cx, cy - 40, 20, cx, cy, R);
    grd.addColorStop(0, '#F6F0E2'); grd.addColorStop(1, '#E2D8C2');
    g.fillStyle = grd; g.beginPath(); g.arc(cx, cy, R, 0, Math.PI * 2); g.fill();
    g.save(); g.beginPath(); g.arc(cx, cy, R - 6, 0, Math.PI * 2); g.clip();
    const s = Math.min((R * 1.8) / inner.width, (R * 1.8) / inner.height);
    g.drawImage(inner, cx - inner.width * s / 2, cy + R * 0.9 - inner.height * s, inner.width * s, inner.height * s);
    g.restore();
    g.strokeStyle = '#7A5A3A'; g.lineWidth = 8; g.beginPath(); g.arc(cx, cy, R, 0, Math.PI * 2); g.stroke();
    stroke(g, [[cx, cy + R], [cx, cy + R + 70]], 12, { seed, dry: 0, color: '#7A5A3A' });
    g.fillStyle = INK.ink; g.font = '64px MaShanZheng'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(label, cx, h - 34);
  });
}
