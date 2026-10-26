// 黏土定格风试作：微缩卧室 + 绵绵（沙袋 = 睡眠压力）+ 钟大爷（闹钟公鸡 = 生物钟）。
// 确定性逐帧：seek(t) 只依赖 t；动作按 12 张/秒量化（定格），每张定格对物体施加微小随机偏移（手工摆拍的抖动）。
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const W = 1080, H = 1920, STOP = 12, END = 4.0;

// ---------------------------------------------------------------- 随机与贴图
function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

// 指纹 + 捏痕凹凸贴图：灰底上叠低频斑块、成组同心弧（指纹）与短刮痕
function clayBump(seed, size = 1024, prints = 60) {
  const cv = document.createElement('canvas');
  cv.width = cv.height = size;
  const g = cv.getContext('2d');
  const r = rng(seed);
  g.fillStyle = '#808080';
  g.fillRect(0, 0, size, size);
  for (let i = 0; i < 900; i++) {
    const x = r() * size, y = r() * size, rad = 8 + r() * 60;
    const grd = g.createRadialGradient(x, y, 0, x, y, rad);
    const v = r() < 0.5 ? 255 : 0;
    grd.addColorStop(0, `rgba(${v},${v},${v},${0.05 + r() * 0.06})`);
    grd.addColorStop(1, `rgba(${v},${v},${v},0)`);
    g.fillStyle = grd;
    g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  for (let i = 0; i < prints; i++) {
    const x = r() * size, y = r() * size, rot = r() * Math.PI, sx = 0.6 + r() * 0.5;
    g.save();
    g.translate(x, y);
    g.rotate(rot);
    g.scale(1, sx);
    for (let k = 3; k < 26; k++) {
      g.beginPath();
      g.arc(0, 0, k * 2.1, -0.4 - r() * 0.6, Math.PI + 0.4 + r() * 0.6);
      g.strokeStyle = `rgba(${k % 2 ? 255 : 0},${k % 2 ? 255 : 0},${k % 2 ? 255 : 0},0.10)`;
      g.lineWidth = 1.1;
      g.stroke();
    }
    g.restore();
  }
  for (let i = 0; i < 160; i++) {
    const x = r() * size, y = r() * size, a = r() * Math.PI * 2, L = 10 + r() * 40;
    g.beginPath();
    g.moveTo(x, y);
    g.lineTo(x + Math.cos(a) * L, y + Math.sin(a) * L);
    g.strokeStyle = 'rgba(0,0,0,0.12)';
    g.lineWidth = 1.5 + r() * 2;
    g.stroke();
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.colorSpace = THREE.NoColorSpace;
  return tex;
}

function weaveBump(size = 512) {
  const cv = document.createElement('canvas');
  cv.width = cv.height = size;
  const g = cv.getContext('2d');
  g.fillStyle = '#808080';
  g.fillRect(0, 0, size, size);
  for (let y = 0; y < size; y += 8) {
    for (let x = 0; x < size; x += 8) {
      const odd = ((x + y) / 8) % 2;
      g.fillStyle = odd ? '#a0a0a0' : '#606060';
      g.fillRect(x, y, odd ? 8 : 6, odd ? 6 : 8);
    }
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(5, 5);
  return tex;
}

const BUMPS = [];
function clay(color, opts = {}) {
  const bump = opts.bump || BUMPS[(opts.seed || 0) % BUMPS.length];
  return new THREE.MeshPhysicalMaterial({
    color, roughness: opts.rough ?? 0.62, metalness: opts.metal ?? 0.0,
    bumpMap: bump, bumpScale: opts.bumpScale ?? 2.6,
    sheen: 0.35, sheenRoughness: 0.8, sheenColor: new THREE.Color(0xffffff),
    clearcoat: opts.coat ?? 0.08, clearcoatRoughness: 0.6,
  });
}

// 捏塑感：沿法线施加低频起伏（不同 seed 形状各异）
function lumpy(geo, amp = 0.05, freq = 2.2, seed = 1) {
  const p = geo.attributes.position, n = geo.attributes.normal;
  const v = new THREE.Vector3(), nn = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    nn.fromBufferAttribute(n, i);
    const s = Math.sin(v.x * freq + seed) * Math.sin(v.y * freq * 1.3 + seed * 2.1) * Math.sin(v.z * freq * 0.8 + seed * 3.7)
      + 0.5 * Math.sin(v.x * freq * 2.7 + seed * 5.3) * Math.sin(v.y * freq * 2.1 + seed);
    v.addScaledVector(nn, amp * s);
    p.setXYZ(i, v.x, v.y, v.z);
  }
  geo.computeVertexNormals();
  return geo;
}

function mesh(geo, mat, parent, pos = [0, 0, 0], rot = [0, 0, 0], scl = [1, 1, 1]) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(...pos);
  m.rotation.set(...rot);
  m.scale.set(...scl);
  m.castShadow = m.receiveShadow = true;
  parent.add(m);
  return m;
}

const ball = (r, seed = 1, amp = 0.04) => lumpy(new THREE.SphereGeometry(r, 48, 32), amp * r, 2.6 / r, seed);
const capsule = (r, len, seed = 1) => lumpy(new THREE.CapsuleGeometry(r, len, 12, 24), 0.05 * r, 2 / r, seed);

function textTexture(text, w, h, font, color, bg) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  const g = cv.getContext('2d');
  if (bg) { g.fillStyle = bg; g.fillRect(0, 0, w, h); }
  g.fillStyle = color;
  g.font = font;
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.fillText(text, w / 2, h / 2 + h * 0.04);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// ---------------------------------------------------------------- 场景
let renderer, scene, camera, composer, bokeh;
const RIG = {};

function buildSet() {
  const wall = clay(0x3a4f96, { seed: 1, bumpScale: 1.8 });
  const floorMat = clay(0x7a4c33, { seed: 2 });
  mesh(new RoundedBoxGeometry(14, 14, 0.6, 4, 0.2), wall, scene, [0, 6.5, -3.0]);
  const floor = mesh(new RoundedBoxGeometry(14, 0.6, 9, 4, 0.2), floorMat, scene, [0, -0.3, 1.2]);
  floor.receiveShadow = true;
  for (let k = -3; k <= 3; k++) mesh(new RoundedBoxGeometry(0.06, 0.05, 9, 2, 0.02), clay(0x4f2f1f, { seed: 3 }), scene, [k * 1.9, 0.01, 1.2]);
  // 地毯
  mesh(lumpy(new THREE.CylinderGeometry(2.6, 2.6, 0.08, 64), 0.03, 2, 7), clay(0xb8524a, { seed: 4 }), scene, [-0.9, 0.04, 1.6], [0, 0, 0], [1, 1, 0.55]);
  mesh(lumpy(new THREE.CylinderGeometry(2.0, 2.0, 0.1, 64), 0.03, 2, 8), clay(0xe0a24c, { seed: 5 }), scene, [-0.9, 0.06, 1.6], [0, 0, 0], [1, 1, 0.55]);

  // 窗：天空为自发光渐变，月亮与星星为黏土粒
  const skyCv = document.createElement('canvas');
  skyCv.width = 64; skyCv.height = 256;
  const sg = skyCv.getContext('2d');
  const grd = sg.createLinearGradient(0, 0, 0, 256);
  grd.addColorStop(0, '#26386f'); grd.addColorStop(0.6, '#8a6aa8'); grd.addColorStop(1, '#ffb978');
  sg.fillStyle = grd; sg.fillRect(0, 0, 64, 256);
  const skyTex = new THREE.CanvasTexture(skyCv);
  skyTex.colorSpace = THREE.SRGBColorSpace;
  const win = new THREE.Group();
  win.position.set(-1.6, 6.6, -2.65);
  scene.add(win);
  const sky = new THREE.Mesh(new THREE.PlaneGeometry(3.0, 3.6), new THREE.MeshBasicMaterial({ map: skyTex }));
  win.add(sky);
  const frameMat = clay(0x8a5a3c, { seed: 6 });
  for (const [x, y, w, h] of [[0, 1.9, 3.5, 0.32], [0, -1.9, 3.7, 0.4], [-1.65, 0, 0.32, 4.0], [1.65, 0, 0.32, 4.0], [0, 0, 0.16, 3.6], [0, 0.2, 3.0, 0.16]])
    mesh(new RoundedBoxGeometry(w, h, 0.3, 3, 0.07), frameMat, win, [x, y, 0.15]);
  const moon = mesh(ball(0.3, 9, 0.03), clay(0xfff0c0, { seed: 7 }), win, [0.75, 1.05, 0.12]);
  moon.material.emissive = new THREE.Color(0xffe2a0); moon.material.emissiveIntensity = 0.25;
  const starMat = clay(0xfff4d0, { seed: 8 });
  starMat.emissive = new THREE.Color(0xfff0c0); starMat.emissiveIntensity = 0.5;
  for (const [x, y] of [[-0.9, 1.3], [-0.4, 0.6], [-1.0, -0.5], [0.4, -0.2], [1.1, 0.4]]) mesh(ball(0.07, x * 10 + y), starMat, win, [x, y, 0.08]);
  // 窗帘
  const curtain = clay(0x8e3a5e, { seed: 9 });
  for (const sx of [-1, 1]) {
    const geo = lumpy(new THREE.CylinderGeometry(0.42, 0.62, 4.6, 24, 12), 0.05, 3, sx * 4);
    mesh(geo, curtain, win, [sx * 2.05, -0.3, 0.45], [0, 0, 0], [1, 1, 0.45]);
    mesh(ball(0.18, sx), clay(0xd9a53a, { seed: 3 }), win, [sx * 2.3, 2.25, 0.4]);
  }
  mesh(capsule(0.08, 4.6, 2), clay(0x4f2f1f, { seed: 2 }), win, [0, 2.25, 0.4], [0, 0, Math.PI / 2]);

  // 床
  const wood = clay(0x8f5a37, { seed: 10 });
  const bed = new THREE.Group();
  bed.position.set(1.9, 0, -1.2);
  scene.add(bed);
  mesh(new RoundedBoxGeometry(3.2, 3.2, 0.4, 5, 0.18), wood, bed, [0, 2.6, -0.9]);
  for (const x of [-1.75, 1.75]) {
    mesh(new RoundedBoxGeometry(0.42, 4.2, 0.42, 4, 0.15), wood, bed, [x, 2.1, -0.9]);
    mesh(ball(0.32, x * 3), wood, bed, [x, 4.42, -0.9]);
  }
  for (const x of [-0.8, 0, 0.8]) mesh(new RoundedBoxGeometry(0.14, 2.2, 0.1, 2, 0.05), clay(0x6a3f25, { seed: 11 }), bed, [x, 2.6, -0.66]);
  mesh(new RoundedBoxGeometry(3.4, 0.9, 4.4, 5, 0.3), clay(0xf3ead6, { seed: 12 }), bed, [0, 0.9, 1.3]);
  const quilt = mesh(lumpy(new RoundedBoxGeometry(3.6, 0.5, 3.4, 6, 0.24), 0.04, 2.5, 3), clay(0xd99a3e, { seed: 13 }), bed, [0, 1.45, 1.8]);
  quilt.rotation.x = 0.02;
  for (const [x, z, c] of [[-0.9, 1.0, 0xb5523e], [0.9, 2.4, 0xb5523e], [0.9, 1.0, 0x5d8a7a], [-0.9, 2.4, 0x5d8a7a]])
    mesh(new RoundedBoxGeometry(1.4, 0.06, 1.1, 2, 0.03), clay(c, { seed: 14 }), bed, [x, 1.72, z]);
  mesh(ball(0.9, 15, 0.03), clay(0xfffaf0, { seed: 15 }), bed, [0, 1.75, -0.2], [0, 0, 0], [1.3, 0.45, 0.7]);

  // 墙上的片名牌
  const plaque = new THREE.Group();
  plaque.position.set(0.2, 10.6, -2.55);
  plaque.rotation.z = -0.03;
  scene.add(plaque);
  mesh(new RoundedBoxGeometry(5.6, 1.35, 0.3, 5, 0.25), clay(0xf2e2bc, { seed: 16 }), plaque);
  const label = new THREE.Mesh(new THREE.PlaneGeometry(5.2, 1.1),
    new THREE.MeshStandardMaterial({ map: textTexture('绵绵与钟大爷', 1040, 220, '900 168px SerifSC', '#c23a2a'), transparent: true, roughness: 0.7,
      bumpMap: BUMPS[0], bumpScale: 1.0 }));
  label.position.z = 0.17;
  plaque.add(label);
  for (const x of [-2.4, 2.4]) mesh(ball(0.12, x), clay(0xd9a53a, { seed: 3 }), plaque, [x, 0.4, 0.2]);
}

function buildSheep() {
  const wool = clay(0xefe6d2, { seed: 20, bumpScale: 2.2 });
  const face = clay(0x54423d, { seed: 21 });
  const dark = clay(0x2a2220, { seed: 22 });
  const sheep = new THREE.Group();
  sheep.position.set(-0.5, 0, 1.9);
  sheep.rotation.y = 0.9;
  sheep.scale.setScalar(0.92);
  scene.add(sheep);
  for (const [x, z] of [[-0.75, 0.45], [-0.75, -0.45], [0.75, 0.45], [0.75, -0.45]]) {
    mesh(capsule(0.2, 0.9, x * 7 + z), face, sheep, [x, 0.75, z]);
    mesh(ball(0.26, x + z), dark, sheep, [x - 0.05, 0.18, z], [0, 0, 0], [1.2, 0.6, 1.0]);
  }
  const torso = new THREE.Group();
  torso.position.set(0, 1.3, 0);
  sheep.add(torso);
  RIG.torso = torso;
  const r = rng(5);
  for (let i = 0; i < 26; i++) {
    const a = r() * Math.PI * 2, b = (r() - 0.5) * 1.6;
    const rad = 0.45 + r() * 0.25;
    mesh(ball(rad, i + 30, 0.06), wool, torso, [Math.cos(a) * 1.0 * Math.cos(b) * 1.15, 0.9 + Math.sin(b) * 0.75, Math.sin(a) * 0.8 * Math.cos(b)]);
  }
  mesh(ball(1.15, 3, 0.05), wool, torso, [0, 0.9, 0], [0, 0, 0], [1.25, 0.85, 0.9]);

  // 沙袋（车床旋转体）+ 绳 + “睡意”吊牌
  const sack = new THREE.Group();
  sack.position.set(0.75, 1.75, -0.2);
  sack.rotation.z = -0.25;
  torso.add(sack);
  RIG.sack = sack;
  const prof = [];
  for (let i = 0; i <= 20; i++) {
    const u = i / 20;
    const rad = 0.05 + 1.25 * Math.sin(Math.PI * Math.min(1, u * 1.15)) ** 0.8 * (1 - 0.35 * u);
    prof.push(new THREE.Vector2(Math.max(0.12, rad), u * 2.4 - 0.2));
  }
  const burlap = clay(0xc49a5c, { bump: weaveBump(), bumpScale: 2.0, rough: 0.85 });
  mesh(lumpy(new THREE.LatheGeometry(prof, 40), 0.07, 2.4, 2), burlap, sack);
  for (const [a, h] of [[-0.5, 0.42], [0.1, 0.5], [0.6, 0.38]]) mesh(capsule(0.1, h, a * 9), burlap, sack, [Math.sin(a) * 0.12, 2.35, Math.cos(a) * 0.05], [0, 0, a]);
  mesh(new THREE.TorusGeometry(0.2, 0.06, 10, 24), clay(0x6b4a28, { seed: 23 }), sack, [0, 2.2, 0], [Math.PI / 2, 0, 0]);
  const tag = new THREE.Group();
  tag.position.set(-0.6, 1.0, 1.05);
  tag.rotation.set(0, -0.95, 0.18);
  sack.add(tag);
  mesh(new RoundedBoxGeometry(1.25, 0.72, 0.1, 3, 0.05), clay(0xf2e2bc, { seed: 24 }), tag);
  const tagTxt = new THREE.Mesh(new THREE.PlaneGeometry(1.15, 0.62),
    new THREE.MeshStandardMaterial({ map: textTexture('睡意', 400, 220, '900 150px SerifSC', '#6b3a1e'), transparent: true, roughness: 0.8 }));
  tagTxt.position.z = 0.06;
  tag.add(tagTxt);
  // 背带
  for (const z of [0.55, -0.55]) mesh(capsule(0.07, 1.3, z * 4), clay(0x7a5630, { seed: 25 }), torso, [-0.15, 1.45, z], [0, 0, -0.9]);

  // 头
  const head = new THREE.Group();
  head.position.set(-1.5, 1.15, 0.2);
  head.scale.setScalar(1.35);
  torso.add(head);
  RIG.head = head;
  mesh(ball(0.62, 40, 0.04), face, head, [0, 0, 0], [0, 0, 0.2], [0.9, 1.05, 0.85]);
  mesh(ball(0.38, 41, 0.03), clay(0x5c4b47, { seed: 26 }), head, [-0.3, -0.38, 0.15], [0, 0, 0], [1.1, 0.8, 1.0]);
  for (const z of [0.05, 0.3]) mesh(ball(0.06, z * 9), dark, head, [-0.6, -0.32, z]);
  for (let i = 0; i < 6; i++) mesh(ball(0.25 + (i % 3) * 0.05, 50 + i, 0.06), wool, head, [0.1 + (i % 3) * 0.18 - 0.2, 0.6 + (i % 2) * 0.12, -0.25 + i * 0.1]);
  for (const s of [-1, 1]) {
    const ear = mesh(ball(0.3, 60 + s, 0.03), face, head, [0.15, 0.25, s * 0.62], [0, 0, 0], [0.5, 0.22, 1.0]);
    ear.rotation.set(s * 0.3, 0, -0.5);
    RIG['ear' + s] = ear;
  }
  RIG.eyes = [];
  for (const z of [-0.18, 0.3]) {
    const eye = new THREE.Group();
    eye.position.set(-0.42, 0.18, z);
    eye.rotation.y = -1.2;
    head.add(eye);
    mesh(ball(0.21, 70 + z, 0.01), clay(0xfbf8f0, { seed: 27, rough: 0.35, coat: 0.5 }), eye);
    const pupil = mesh(ball(0.085, 71, 0.0), clay(0x111111, { seed: 28, rough: 0.2, coat: 0.8 }), eye, [0, -0.04, 0.17]);
    const lid = mesh(new THREE.SphereGeometry(0.225, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), face, eye);
    RIG.eyes.push({ pupil, lid });
  }
  const mouth = mesh(ball(0.14, 80, 0.02), clay(0x6e1c22, { seed: 29 }), head, [-0.55, -0.5, 0.12], [0, 0, 0], [0.8, 1, 1]);
  RIG.mouth = mouth;
  // 睡帽
  const cap = new THREE.Group();
  cap.position.set(0.1, 0.62, 0.0);
  cap.rotation.z = -1.0;
  head.add(cap);
  const capMat = clay(0x4f6bc9, { seed: 30 });
  mesh(lumpy(new THREE.ConeGeometry(0.55, 1.6, 48, 24), 0.03, 3, 4), capMat, cap, [0, 0.7, 0]);
  mesh(lumpy(new THREE.TorusGeometry(0.5, 0.1, 12, 32), 0.01, 4, 5), clay(0xf6f2ea, { seed: 31 }), cap, [0, 0.0, 0], [Math.PI / 2, 0, 0]);
  mesh(ball(0.2, 82), clay(0xffffff, { seed: 32, bumpScale: 2.5 }), cap, [0, 1.55, 0]);
  // 手臂 + 手套
  const arm = mesh(capsule(0.16, 1.0, 9), face, torso, [-1.05, 0.25, 0.75], [0, 0, -0.35]);
  RIG.arm = arm;
  mesh(ball(0.26, 90, 0.04), clay(0xfffdf6, { seed: 33 }), torso, [-1.25, -0.35, 0.8]);
  RIG.sheep = sheep;
}

function buildRooster() {
  const red = clay(0xc8402e, { seed: 40 });
  const orange = clay(0xe07436, { seed: 41 });
  const yellow = clay(0xf0c040, { seed: 42 });
  const brass = clay(0xd9a53a, { seed: 43, rough: 0.4, metal: 0.25, coat: 0.3 });
  const cream = clay(0xf6ecd2, { seed: 44 });
  const ro = new THREE.Group();
  ro.position.set(1.75, 4.72, -1.0);
  ro.rotation.y = -0.3;
  ro.scale.setScalar(0.85);
  scene.add(ro);
  RIG.rooster = ro;
  for (const x of [-0.3, 0.3]) {
    mesh(capsule(0.07, 0.5, x * 9), orange, ro, [x, 0.3, 0]);
    for (const a of [-0.6, 0, 0.6]) mesh(capsule(0.045, 0.3, a), orange, ro, [x + Math.sin(a) * 0.15, 0.03, Math.cos(a) * 0.15], [Math.PI / 2, 0, -a]);
  }
  const body = new THREE.Group();
  body.position.set(0, 1.45, 0);
  ro.add(body);
  RIG.rbody = body;
  // 尾羽
  for (const [c, a] of [[0x2e8c8a, 0.9], [0x1f5f6a, 0.5], [0xe07436, 0.15]])
    mesh(ball(0.5, a * 10, 0.04), clay(c, { seed: 45 }), body, [0.85 + Math.cos(a) * 0.3, 0.5 + Math.sin(a) * 0.6, -0.4], [0, 0, a - 0.6], [1.6, 0.4, 0.3]);
  // 闹钟肚子
  mesh(lumpy(new THREE.CylinderGeometry(1.05, 1.05, 0.75, 48, 4), 0.03, 2.5, 6), red, body, [0, 0, 0], [Math.PI / 2, 0, 0]);
  mesh(lumpy(new THREE.CylinderGeometry(0.86, 0.86, 0.1, 48, 2), 0.01, 3, 7), cream, body, [0, 0, 0.39], [Math.PI / 2, 0, 0]);
  for (let k = 0; k < 12; k++) {
    const a = k * Math.PI / 6;
    mesh(new RoundedBoxGeometry(k % 3 ? 0.06 : 0.09, k % 3 ? 0.14 : 0.22, 0.05, 2, 0.02), clay(0x2a2220, { seed: 46 }), body,
      [Math.sin(a) * 0.68, Math.cos(a) * 0.68, 0.46], [0, 0, -a]);
  }
  RIG.hands = [];
  for (const [len, w] of [[0.45, 0.1], [0.66, 0.06]]) {
    const piv = new THREE.Group();
    piv.position.set(0, 0, 0.47);
    body.add(piv);
    mesh(new RoundedBoxGeometry(w, len, 0.05, 2, 0.02), clay(0x2a2220, { seed: 47 }), piv, [0, len / 2 - 0.05, 0]);
    RIG.hands.push(piv);
  }
  mesh(ball(0.08, 48), red, body, [0, 0, 0.5]);
  for (const x of [-0.62, 0.62]) mesh(ball(0.36, x * 5, 0.02), brass, body, [x, 0.98, -0.05], [0, 0, x * 0.4], [1, 0.75, 1]);
  // 头
  const head = new THREE.Group();
  head.position.set(0, 1.55, 0.1);
  body.add(head);
  RIG.rhead = head;
  mesh(ball(0.5, 50, 0.04), orange, head);
  for (const [x, y, r] of [[-0.2, 0.5, 0.17], [0.0, 0.6, 0.2], [0.2, 0.52, 0.17]]) mesh(ball(r, x * 20 + 3, 0.05), red, head, [x, y, 0]);
  const beakU = mesh(lumpy(new THREE.ConeGeometry(0.17, 0.5, 16, 3), 0.01, 4, 2), yellow, head, [-0.55, -0.02, 0.22], [0, 0, Math.PI / 2 + 0.2]);
  const beakL = mesh(lumpy(new THREE.ConeGeometry(0.13, 0.4, 16, 3), 0.01, 4, 3), yellow, head, [-0.5, -0.18, 0.22], [0, 0, Math.PI / 2 - 0.4]);
  RIG.beak = [beakU, beakL];
  mesh(ball(0.13, 51), red, head, [-0.42, -0.35, 0.2], [0, 0, 0], [0.8, 1.3, 0.8]);
  mesh(ball(0.15, 52, 0.01), clay(0xfbf8f0, { seed: 49, rough: 0.35, coat: 0.5 }), head, [-0.32, 0.12, 0.35]);
  mesh(ball(0.07, 53, 0), clay(0x111111, { seed: 50, rough: 0.2, coat: 0.8 }), head, [-0.4, 0.1, 0.46]);
  mesh(capsule(0.045, 0.3, 54), clay(0x2a2220, { seed: 51 }), head, [-0.33, 0.33, 0.42], [0, 0, -1.2]);
  // 翅膀手臂 + 手套 + 镲
  RIG.arms = [];
  for (const s of [-1, 1]) {
    const sh = new THREE.Group();
    sh.position.set(s * 0.95, 0.5, 0.1);
    body.add(sh);
    const arm = mesh(capsule(0.12, 0.7, s * 3), orange, sh, [s * 0.45, 0.2, 0], [0, 0, s * 1.1]);
    const hand = new THREE.Group();
    hand.position.set(s * 0.9, 0.45, 0.15);
    sh.add(hand);
    mesh(ball(0.2, 60 + s, 0.04), clay(0xfffdf6, { seed: 52 }), hand);
    const cym = mesh(lumpy(new THREE.CylinderGeometry(0.75, 0.75, 0.05, 48, 2), 0.01, 3, s), brass, hand, [s * 0.15, 0, 0], [0, 0, Math.PI / 2]);
    mesh(ball(0.12, 62, 0.01), brass, cym, [0, 0.06, 0]);
    RIG.arms.push({ sh, arm, hand, s });
  }
}

function buildBurst() {
  // “当！”拟声：黄色锯齿片 + 红字，只在敲击定格出现
  const g = new THREE.Group();
  g.position.set(-0.6, 8.5, -0.3);
  scene.add(g);
  const shp = new THREE.Shape();
  for (let k = 0; k < 22; k++) {
    const a = Math.PI * k / 11, rr = k % 2 ? 0.85 : 1.35;
    const x = Math.cos(a) * rr * 1.1, y = Math.sin(a) * rr;
    k ? shp.lineTo(x, y) : shp.moveTo(x, y);
  }
  mesh(new THREE.ExtrudeGeometry(shp, { depth: 0.18, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.05, bevelSegments: 3 }),
    clay(0xffd84a, { seed: 60 }), g);
  const t = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 1.1),
    new THREE.MeshStandardMaterial({ map: textTexture('当！', 400, 220, '900 170px SerifSC', '#c23a2a'), transparent: true, roughness: 0.7 }));
  t.position.z = 0.26;
  g.add(t);
  RIG.burst = g;
}

// ---------------------------------------------------------------- 动作（定格量化）
const ease = x => 1 - (1 - x) ** 3;
function pose(t) {
  const k = Math.floor(t * STOP);
  const tq = k / STOP;
  const r = rng(1000 + k);
  const jit = (o, a) => { o.position.x += (r() - 0.5) * a; o.position.y += (r() - 0.5) * a; o.rotation.z += (r() - 0.5) * a * 0.5; };
  // 敲镲：每 2 秒一次，0.15 秒合拢 → 撞开
  const ph = (tq + 1.6) % 2.0;
  const close = ph < 0.35 ? ph / 0.35 : 0;
  const hit = ph >= 0.35 ? Math.exp(-(ph - 0.35) * 2.2) : 0;
  const crash = ph < 0.35 ? 1 - ease(close) : 0.25 + 0.75 * ease(Math.min(1, (ph - 0.35) / 0.15));
  for (const { sh, hand, s } of RIG.arms) {
    sh.rotation.z = s * (-0.9 + 1.1 * crash);
    hand.rotation.z = s * 0.3 * crash;
  }
  RIG.rbody.scale.set(1 - 0.06 * hit, 1 + 0.08 * hit, 1);
  RIG.rbody.position.y = 1.45 + 0.1 * hit;
  RIG.rhead.rotation.z = -0.25 * hit;
  RIG.beak[0].rotation.z = Math.PI / 2 + 0.2 + 0.35 * hit;
  RIG.beak[1].rotation.z = Math.PI / 2 - 0.4 - 0.45 * hit;
  const hour = 7 + tq / 60;
  RIG.hands[0].rotation.z = -(hour % 12) / 12 * Math.PI * 2;
  RIG.hands[1].rotation.z = -(hour % 1) * Math.PI * 2;
  RIG.burst.visible = hit > 0.35;
  RIG.burst.scale.setScalar(0.85 + 0.35 * hit);
  RIG.burst.rotation.z = -0.12 + 0.1 * hit;
  // 绵绵：沙袋压弯；被敲醒时整个人弹一下、眼皮睁开
  const jolt = hit;
  RIG.torso.rotation.z = 0.32 - 0.22 * jolt;
  RIG.torso.scale.set(1 + 0.05 * jolt, 1 - 0.06 * jolt + 0.03 * Math.sin(tq * 3), 1);
  RIG.head.rotation.z = 0.18 - 0.2 * jolt;
  const lid = 0.5 - 0.45 * jolt;
  for (const { lid: l, pupil } of RIG.eyes) {
    l.rotation.x = (lid - 0.5) * Math.PI;
    pupil.position.y = -0.04 + 0.05 * jolt;
  }
  const yawn = Math.max(0, 1 - jolt * 2) * (0.6 + 0.4 * Math.sin(tq * 2));
  RIG.mouth.scale.set(0.8, 0.5 + 1.1 * yawn, 1);
  RIG.ear1.rotation.z = -0.5 + 0.6 * jolt;
  RIG['ear-1'].rotation.z = -0.5 + 0.6 * jolt;
  RIG.sack.scale.setScalar(1 + 0.02 * Math.sin(tq * 4));
  // 手工摆拍的抖动
  jit(RIG.sheep, 0.012);
  jit(RIG.rooster, 0.012);
  jit(RIG.burst, 0.03);
  for (const b of BUMPS) b.offset.set((k % 3) * 0.003, (k % 2) * 0.003);
  document.getElementById('cap').textContent = '通宵到清晨，钟大爷开始推你了';
}

function resetJitter() {
  RIG.sheep.position.set(-0.5, 0, 1.9);
  RIG.sheep.rotation.z = 0;
  RIG.rooster.position.set(1.75, 4.72, -1.0);
  RIG.rooster.rotation.z = 0;
  RIG.burst.position.set(-0.6, 8.5, -0.3);
}

// ---------------------------------------------------------------- 启动
async function boot() {
  await document.fonts.load('900 100px SerifSC');
  await document.fonts.load('900 60px SC');
  BUMPS.push(clayBump(1), clayBump(2), clayBump(3));
  renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.3;
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1b1530);
  camera = new THREE.PerspectiveCamera(34, W / H, 0.5, 100);
  camera.position.set(0.2, 6.6, 24.5);
  camera.lookAt(0.2, 5.0, 0);

  scene.add(new THREE.HemisphereLight(0x8090e0, 0x3a2028, 0.9));
  const key = new THREE.DirectionalLight(0xffc98a, 2.6);
  key.position.set(7, 12, 10);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -9, right: 9, top: 13, bottom: -3, near: 1, far: 40 });
  key.shadow.bias = -0.0004;
  key.shadow.radius = 4;
  scene.add(key);
  const rim = new THREE.DirectionalLight(0x8fb0ff, 1.3);
  rim.position.set(-8, 8, -6);
  scene.add(rim);
  const fillL = new THREE.DirectionalLight(0xffe2c8, 0.9);
  fillL.position.set(-2, 4, 20);
  scene.add(fillL);
  const dawn = new THREE.PointLight(0xffa860, 30, 12, 1.6);
  dawn.position.set(-1.6, 5.8, -1.2);
  scene.add(dawn);

  buildSet();
  buildSheep();
  buildRooster();
  buildBurst();

  composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  bokeh = new BokehPass(scene, camera, { focus: 22.6, aperture: 0.0018, maxblur: 0.006 });
  composer.addPass(bokeh);
  composer.addPass(new OutputPass());
  window.AC.ready = true;
}

window.AC = {
  ready: false, error: null,
  info: () => ({ end: END }),
  seek(t) {
    resetJitter();
    pose(t);
    composer.render();
  },
};
boot().catch(e => { window.AC.error = String(e && e.stack || e); console.error(e); });
