// 国风 3D 渲染引擎：确定性逐帧（seek(t) 只依赖 t）、每个镜头一个独立场景、DOM 字幕层、2D 水墨特效层。
// 时间轴（实测拍点、镜头起止、动作时刻）由 Python 生成 timeline.json 后注入，JS 不自行估计节拍。
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export { THREE, RoundedBoxGeometry };
export const W = 1080, H = 1920;

// 中国传统色（近似）：宣纸、墨、朱砂、石青、石绿、赭石、藤黄、檀木
export const PAL = {
  paper: '#EFE6D3', paper2: '#E2D3B6', paperDark: '#CDBB98',
  ink: '#2A2622', ink2: '#5A5048', ink3: '#8C8070',
  cinnabar: '#C23A2B', vermilion: '#DA5A2E', rouge: '#A8322D',
  azure: '#2D5C7A', azure2: '#4F82A0', jade: '#3C8C7A', jade2: '#7DB5A2',
  ochre: '#B5763C', gamboge: '#E3A93B', gold: '#C8A15E',
  wood: '#7A4A30', wood2: '#9E6A45', wood3: '#C9986A', bamboo: '#6F9A58',
  tile: '#3F4A55', white: '#F8F2E7', cold: '#7EC6E6', cold2: '#BFE6F4', heat: '#E8733A', heat2: '#F2A65A',
};

// ---------------------------------------------------------------- 数学与缓动
export const clamp01 = x => (x < 0 ? 0 : x > 1 ? 1 : x);
export const lerp = (a, b, k) => a + (b - a) * k;
export const easeOut = x => 1 - Math.pow(1 - clamp01(x), 3);
export const easeIn = x => Math.pow(clamp01(x), 3);
export const easeInOut = x => { x = clamp01(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
export const easeOutBack = (x, s = 1.7) => { x = clamp01(x) - 1; return 1 + (s + 1) * x * x * x + s * x * x; };
export const prog = (t, a, d) => (d > 0 ? clamp01((t - a) / d) : (t >= a ? 1 : 0));
export const win = (t, a, b, fi = 0.25, fo = 0.3) => (t < a || t > b ? 0 : Math.min(prog(t, a, fi), 1 - prog(t, b - fo, fo)));
/** 撞击脉冲：t0 起的衰减振荡，用于挤压回弹（0 → 1 → 0）。 */
export const pulse = (t, t0, decay = 7, freq = 18) => (t < t0 ? 0 : Math.exp(-(t - t0) * decay) * Math.cos((t - t0) * freq));
export const bump = (t, t0, decay = 6) => (t < t0 ? 0 : Math.exp(-(t - t0) * decay));

export function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) % 1e9) / 1e9; };
}

// ---------------------------------------------------------------- 时间轴
export const TL = { beats: [], shots: [], cues: {}, end: 0, music_end: 0 };
export function loadTimeline(data) { Object.assign(TL, data); }
/** 动作时刻（全片秒数）；名字写错直接抛错，避免静默错位。 */
export function cue(name) {
  if (!(name in TL.cues)) throw new Error('unknown cue ' + name);
  return TL.cues[name];
}
export const since = (t, name) => t - cue(name);
export const P = (t, name, d = 0.45, ease = easeOut) => ease(prog(t, cue(name), d));

// ---------------------------------------------------------------- 渲染器
export let renderer = null;
export function initRenderer(canvas) {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.setClearColor(0x000000, 0);
  return renderer;
}

export function lights(scene, { key = [6, 10, 7], intensity = 2.4, hemi = 0.9, color = '#FFF1DA', fill = '#BCD3E0',
  shadow = 12, map = 2048 } = {}) {
  scene.add(new THREE.HemisphereLight('#FFF8EC', '#8A7A62', hemi));
  const d = new THREE.DirectionalLight(color, intensity);
  d.position.set(...key);
  d.castShadow = true;
  d.shadow.mapSize.set(map, map);
  const c = d.shadow.camera;
  c.left = -shadow; c.right = shadow; c.top = shadow; c.bottom = -shadow; c.near = 0.5; c.far = 60;
  d.shadow.bias = -0.0004;
  d.shadow.normalBias = 0.025;
  d.shadow.radius = 4;
  scene.add(d);
  const f = new THREE.DirectionalLight(fill, 0.55);
  f.position.set(-key[0], key[1] * 0.6, key[2] * 0.4);
  scene.add(f);
  return d;
}

// ---------------------------------------------------------------- 材质
const _mats = new Map();
/** 哑光陶土 / 纸塑质感（国风 3D 插画的主材质）。 */
export function clay(color, rough = 0.82, extra = {}) {
  const key = 'c' + color + rough + JSON.stringify(extra);
  if (!_mats.has(key)) _mats.set(key, new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0.0, ...extra }));
  return _mats.get(key);
}
/** 漆器质感：朱漆、黑漆，带清漆高光。 */
export function lacquer(color, rough = 0.32) {
  const key = 'l' + color + rough;
  if (!_mats.has(key)) _mats.set(key, new THREE.MeshPhysicalMaterial({ color, roughness: rough, clearcoat: 0.8, clearcoatRoughness: 0.25 }));
  return _mats.get(key);
}
export function metal(color, rough = 0.38) {
  const key = 'm' + color + rough;
  if (!_mats.has(key)) _mats.set(key, new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0.75 }));
  return _mats.get(key);
}
export function glow(color, intensity = 1.0) {
  return new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: intensity, roughness: 0.6 });
}
const _inkMat = new THREE.MeshBasicMaterial({ color: PAL.ink, side: THREE.BackSide });
/** 墨线描边（反向外壳法）：在网格外套一层略大的背面墨色壳。 */
export function outline(mesh, thick = 0.035, color = null) {
  const m = color ? new THREE.MeshBasicMaterial({ color, side: THREE.BackSide }) : _inkMat;
  const o = new THREE.Mesh(mesh.geometry, m);
  o.scale.setScalar(1 + thick);
  o.userData.outline = true;
  mesh.add(o);
  return mesh;
}

export function mesh(geo, mat, { cast = true, receive = true, ink = 0 } = {}) {
  const m = new THREE.Mesh(geo, mat);
  m.castShadow = cast;
  m.receiveShadow = receive;
  if (ink) outline(m, ink);
  return m;
}
export const box = (w, h, d, mat, r = 0, o = {}) => mesh(r > 0 ? new RoundedBoxGeometry(w, h, d, 4, r) : new THREE.BoxGeometry(w, h, d), mat, o);
export const cyl = (rt, rb, h, mat, seg = 40, o = {}) => mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat, o);
export const sphere = (r, mat, o = {}) => mesh(new THREE.SphereGeometry(r, 40, 24), mat, o);
export const torus = (r, tube, mat, arc = Math.PI * 2, o = {}) => mesh(new THREE.TorusGeometry(r, tube, 20, 80, arc), mat, o);

export function group(...children) {
  const g = new THREE.Group();
  children.forEach(c => c && g.add(c));
  return g;
}
export function at(obj, x = 0, y = 0, z = 0, ry = 0, s = 1) {
  obj.position.set(x, y, z);
  obj.rotation.y = ry;
  if (s !== 1) obj.scale.setScalar(s);
  return obj;
}

/** 只接收阴影的透明地面：3D 物件像摆在宣纸上。 */
export function shadowFloor(size = 40, opacity = 0.22) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.ShadowMaterial({ opacity, color: '#3A2A18' }));
  m.rotation.x = -Math.PI / 2;
  m.receiveShadow = true;
  return m;
}

// ---------------------------------------------------------------- 画布纹理（水墨远山、祥云、文字）
export function canvasTex(w, h, draw) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  draw(cv.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

/** 水墨远山：多层山脊剪影，自上而下由浓转淡（留白），seed 控制山形。 */
export function inkMountainsTex(seed = 1, { w = 2048, h = 1024, layers = 3, tint = '#3B4A4E' } = {}) {
  return canvasTex(w, h, (g) => {
    const r = rng(seed * 977);
    for (let L = 0; L < layers; L++) {
      const base = h * (0.42 + L * 0.14);
      const amp = h * (0.26 - L * 0.06);
      const alpha = 0.22 + L * 0.2;
      g.beginPath();
      g.moveTo(0, h);
      const n = 9 + L * 3;
      const peaks = Array.from({ length: n + 1 }, () => r());
      for (let x = 0; x <= w; x += 6) {
        const u = x / w * n, i = Math.floor(u), f = u - i;
        const a = peaks[i], b = peaks[Math.min(n, i + 1)];
        const s = a + (b - a) * (0.5 - 0.5 * Math.cos(f * Math.PI));
        const y = base - amp * Math.pow(s, 1.6) - amp * 0.08 * Math.sin(x * 0.03 + L);
        g.lineTo(x, y);
      }
      g.lineTo(w, h);
      g.closePath();
      const grd = g.createLinearGradient(0, base - amp, 0, base + h * 0.25);
      grd.addColorStop(0, hexA(tint, alpha));
      grd.addColorStop(0.55, hexA(tint, alpha * 0.45));
      grd.addColorStop(1, hexA(tint, 0));
      g.fillStyle = grd;
      g.fill();
    }
  });
}

export function hexA(hex, a) {
  const c = new THREE.Color(hex);
  return `rgba(${Math.round(c.r * 255)},${Math.round(c.g * 255)},${Math.round(c.b * 255)},${a})`;
}

/** 祥云轮廓（用于 ExtrudeGeometry）：三个卷云头 + 云尾。 */
export function cloudShape(s = 1) {
  const sh = new THREE.Shape();
  const arc = (cx, cy, r, a0, a1, ccw = false) => sh.absarc(cx * s, cy * s, r * s, a0, a1, ccw);
  sh.moveTo(-1.6 * s, 0);
  arc(-1.05, 0.15, 0.55, Math.PI, 0.15 * Math.PI, true);
  arc(-0.1, 0.42, 0.62, 0.95 * Math.PI, 0.05 * Math.PI, true);
  arc(0.85, 0.12, 0.5, 0.9 * Math.PI, -0.1 * Math.PI, true);
  sh.quadraticCurveTo(1.9 * s, -0.25 * s, 2.3 * s, -0.05 * s);
  sh.quadraticCurveTo(1.6 * s, -0.42 * s, 0.6 * s, -0.36 * s);
  sh.lineTo(-1.6 * s, -0.36 * s);
  sh.quadraticCurveTo(-1.95 * s, -0.2 * s, -1.6 * s, 0);
  return sh;
}
export function cloud3d(s = 1, color = PAL.white, depth = 0.18) {
  const geo = new THREE.ExtrudeGeometry(cloudShape(s), { depth: depth * s, bevelEnabled: true, bevelThickness: 0.05 * s,
    bevelSize: 0.05 * s, bevelSegments: 3, curveSegments: 24 });
  geo.center();
  return mesh(geo, clay(color, 0.7), { ink: 0.0 });
}

/** 3D 文字牌：把文字画到画布纹理贴在平面上（用于卷轴、牌匾、算盘标签等）。 */
export function textPlane(text, { font = 'MaShanZheng', size = 120, color = PAL.ink, w = 4, h = 1, px = 512,
  weight = 400, bg = null, align = 'center' } = {}) {
  const pw = Math.round(px * w / h), ph = px;
  const tex = canvasTex(pw, ph, (g) => {
    if (bg) { g.fillStyle = bg; g.fillRect(0, 0, pw, ph); }
    g.fillStyle = color;
    g.font = `${weight} ${size}px "${font}"`;
    g.textAlign = align;
    g.textBaseline = 'middle';
    g.fillText(text, align === 'center' ? pw / 2 : 20, ph / 2);
  });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, transparent: true }));
  return m;
}

// ---------------------------------------------------------------- 宣纸底
export function paintPaper(canvas, tint = PAL.paper) {
  const g = canvas.getContext('2d');
  g.fillStyle = tint;
  g.fillRect(0, 0, W, H);
  const r = rng(7);
  for (let i = 0; i < 2600; i++) {             // 纸纤维
    const x = r() * W, y = r() * H, l = 6 + r() * 26, a = r() * Math.PI;
    g.strokeStyle = `rgba(120,96,60,${0.03 + r() * 0.05})`;
    g.lineWidth = 0.6 + r() * 0.8;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
  }
  for (let i = 0; i < 18; i++) {                // 淡墨晕
    const x = r() * W, y = r() * H, rad = 120 + r() * 380;
    const grd = g.createRadialGradient(x, y, 0, x, y, rad);
    grd.addColorStop(0, `rgba(150,120,80,${0.03 + r() * 0.04})`);
    grd.addColorStop(1, 'rgba(150,120,80,0)');
    g.fillStyle = grd; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  const v = g.createRadialGradient(W / 2, H * 0.45, H * 0.25, W / 2, H * 0.45, H * 0.78);
  v.addColorStop(0, 'rgba(60,40,20,0)');
  v.addColorStop(1, 'rgba(60,40,20,0.28)');
  g.fillStyle = v; g.fillRect(0, 0, W, H);
}

// ---------------------------------------------------------------- 水墨特效层（转场墨刷、撞击墨点）
export function inkWipe(g, k, dir = 1, color = PAL.ink, seed = 3) {
  // k: 0→1 覆盖，1→2 揭开；墨刷带边缘有飞白锯齿
  if (k <= 0 || k >= 2) return;
  const r = rng(seed);
  const bands = 7;
  for (let b = 0; b < bands; b++) {
    const y0 = H * b / bands - 40, hh = H / bands + 80;
    const lag = r() * 0.25;
    const cover = clamp01((k - lag) / (1 - 0.25));
    const reveal = clamp01((k - 1 - lag) / (1 - 0.25));
    const x0 = easeInOut(reveal) * (W + 300) - 150, x1 = easeInOut(cover) * (W + 300) - 150;
    const a = dir > 0 ? x0 : W - x1, c = dir > 0 ? x1 : W - x0;
    if (c - a <= 0) continue;
    g.fillStyle = color;
    g.beginPath();
    g.moveTo(a, y0);
    for (let x = a; x <= c; x += 30) g.lineTo(x, y0 + 14 * Math.sin(x * 0.02 + b) + r() * 10);
    for (let x = c; x >= a; x -= 30) g.lineTo(x, y0 + hh - 14 * Math.cos(x * 0.018 + b) - r() * 10);
    g.closePath();
    g.fill();
  }
}

export function inkSplash(g, x, y, dt, rad = 120, color = PAL.cinnabar, seed = 5, dur = 0.6) {
  if (dt < 0 || dt > dur) return;
  const k = easeOut(dt / 0.18), a = 1 - clamp01((dt - 0.25) / (dur - 0.25));
  const r = rng(seed);
  g.fillStyle = hexA(color, 0.85 * a);
  for (let i = 0; i < 14; i++) {
    const ang = r() * Math.PI * 2, d = rad * (0.4 + r() * 0.9) * k, s = (6 + r() * 16) * (1 - 0.4 * k);
    g.beginPath(); g.arc(x + Math.cos(ang) * d, y + Math.sin(ang) * d, s, 0, Math.PI * 2); g.fill();
  }
}

// ---------------------------------------------------------------- 屏幕投影（3D 点 → 画面像素，用于标签跟随）
const _v = new THREE.Vector3();
export function toScreen(obj, camera, offset = [0, 0, 0]) {
  obj.updateWorldMatrix(true, false);
  _v.set(...offset).applyMatrix4(obj.matrixWorld).project(camera);
  return [(_v.x + 1) / 2 * W, (1 - _v.y) / 2 * H];
}

// ---------------------------------------------------------------- 镜头运动
/** 相机关键帧：keys=[{t, pos:[x,y,z], look:[x,y,z], fov}]（镜头内秒数），相邻关键帧之间缓入缓出插值。 */
export function camKeys(camera, lt, keys) {
  let a = keys[0], b = keys[keys.length - 1];
  for (let i = 0; i < keys.length - 1; i++) if (lt >= keys[i].t && lt <= keys[i + 1].t) { a = keys[i]; b = keys[i + 1]; break; }
  if (lt < keys[0].t) b = a;
  const k = b === a ? 0 : easeInOut((lt - a.t) / (b.t - a.t));
  const L = (u, v) => u.map((x, j) => lerp(x, v[j], k));
  const p = L(a.pos, b.pos), l = L(a.look, b.look);
  camera.position.set(...p);
  camera.lookAt(...l);
  const fov = lerp(a.fov || 35, b.fov || 35, k);
  if (camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
}

export function makeCamera(fov = 35) {
  const c = new THREE.PerspectiveCamera(fov, W / H, 0.1, 200);
  return c;
}

/** 镜头震动：在撞击拍点后 0.35 秒内对相机做衰减抖动（确定性）。 */
export function shake(camera, t, t0, amp = 0.08) {
  if (t < t0 || t > t0 + 0.4) return;
  const k = Math.exp(-(t - t0) * 9) * amp;
  camera.position.x += Math.sin((t - t0) * 61) * k;
  camera.position.y += Math.cos((t - t0) * 47) * k;
}
