// 3D 渲染引擎：确定性逐帧（seek(t) 只依赖 t）、DOM 字幕层、2D 淡入淡出层。
// 时间轴（实测拍点、镜头起止、动作时刻）由 Python 生成 timeline.json 后注入，JS 不自行估计节拍。
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export { THREE, RoundedBoxGeometry };
export const W = 1080, H = 1920;

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

// ---------------------------------------------------------------- 材质
const _mats = new Map();
/** 哑光材质（墙面、布艺、木头等）。 */
export function clay(color, rough = 0.82, extra = {}) {
  const key = 'c' + color + rough + JSON.stringify(extra);
  if (!_mats.has(key)) _mats.set(key, new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0.0, ...extra }));
  return _mats.get(key);
}
export function metal(color, rough = 0.38) {
  const key = 'm' + color + rough;
  if (!_mats.has(key)) _mats.set(key, new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0.75 }));
  return _mats.get(key);
}
export function mesh(geo, mat, { cast = true, receive = true } = {}) {
  const m = new THREE.Mesh(geo, mat);
  m.castShadow = cast;
  m.receiveShadow = receive;
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

/** 只接收阴影的透明地面：屋子像摆在浅色背景上。 */
export function shadowFloor(size = 40, opacity = 0.22) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.ShadowMaterial({ opacity, color: '#24313D' }));
  m.rotation.x = -Math.PI / 2;
  m.receiveShadow = true;
  return m;
}

// ---------------------------------------------------------------- 画布纹理
export function canvasTex(w, h, draw) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  draw(cv.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

export function makeCamera(fov = 35) {
  return new THREE.PerspectiveCamera(fov, W / H, 0.1, 200);
}
