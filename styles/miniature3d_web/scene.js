// 真 3D 微缩办公室样片：一座漂浮的黏土小岛（工位、电脑、小人、挂钟、大书本与弹簧），一台相机连续运镜、不硬切。
// 所有画面是本地时间 t 的纯函数；时间轴（8 小节、实测拍点、原片音效拍、文案）由 styles/miniature3d.py 写入 timeline.json。
import {
  THREE, W, H, clamp01, lerp, easeOut, easeIn, easeInOut, easeOutBack, prog, pulse, bump,
  initRenderer, clay, mesh, box, cyl, sphere, torus, group, at, shadowFloor, canvasTex, makeCamera,
} from '../../ac3d/web/engine.js';
import { wallClock } from '../../ac3d/web/room.js';

let TLD = null;
const B = (i, k) => {                                   // 第 i 小节第 k 拍（可小数）的本地秒数
  const b = TLD.bars[i];
  const arr = [...b.beats, b.t1];
  const j = Math.floor(k), f = k - j;
  return arr[j] + (arr[Math.min(j + 1, 4)] - arr[j]) * f;
};

// ---------------------------------------------------------------- 黏土小人（原点脚底，面朝 +z）
function chibi(shirt, { hair = '#2A2420', pants = '#33384A', suit = false, long = false } = {}) {
  const g = new THREE.Group();
  const skin = clay('#F2CDA8', 0.75);
  const body = new THREE.Group();
  g.add(body);
  const torso = mesh(new THREE.CapsuleGeometry(0.2, 0.28, 8, 20), clay(shirt, 0.85));
  torso.position.y = 0.72;
  body.add(torso);
  if (suit) {
    const tie = box(0.06, 0.24, 0.02, clay('#C8332E', 0.6), 0.01);
    tie.position.set(0, 0.78, 0.2);
    body.add(tie);
  }
  const head = new THREE.Group();
  head.add(sphere(0.25, skin));
  const cap = mesh(new THREE.SphereGeometry(0.262, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.55), clay(hair, 0.85));
  cap.rotation.x = -0.45;
  head.add(cap);
  if (long) {
    const back = mesh(new THREE.CapsuleGeometry(0.22, 0.22, 6, 16), clay(hair, 0.85));
    back.position.set(0, -0.12, -0.08);
    head.add(back);
  }
  for (const s of [-1, 1]) {
    const eye = sphere(0.032, clay('#1E1C22', 0.4));
    eye.position.set(0.09 * s, 0.0, 0.23);
    head.add(eye);
    const blush = sphere(0.04, clay('#F09A8A', 0.9));
    blush.scale.set(1, 0.6, 0.4);
    blush.position.set(0.15 * s, -0.07, 0.2);
    head.add(blush);
  }
  head.position.y = 1.17;
  body.add(head);
  const limb = (r, l, mat, x, y) => {
    const p = new THREE.Group();
    const m = mesh(new THREE.CapsuleGeometry(r, l, 6, 14), mat);
    m.position.y = -l / 2 - r;
    p.add(m);
    p.position.set(x, y, 0);
    body.add(p);
    return p;
  };
  const armL = limb(0.06, 0.26, clay(shirt, 0.85), -0.25, 0.9);
  const armR = limb(0.06, 0.26, clay(shirt, 0.85), 0.25, 0.9);
  const legL = limb(0.075, 0.28, clay(pants, 0.85), -0.1, 0.45);
  const legR = limb(0.075, 0.28, clay(pants, 0.85), 0.1, 0.45);
  g.userData = {
    head, body,
    pose({ walk = 0, amp = 0, up = 0, jump = 0, slump = 0, wave = 0, squash = 0 } = {}) {
      const sw = Math.sin(walk * Math.PI) * amp;
      legL.rotation.x = sw * 0.6;
      legR.rotation.x = -sw * 0.6;
      armL.rotation.x = -sw * 0.5;
      armR.rotation.x = sw * 0.5;
      armL.rotation.z = -up * 2.6 - slump * 0.1;
      armR.rotation.z = up * 2.6 + wave * 2.4 + slump * 0.1;
      body.position.y = jump;
      head.rotation.x = slump * 0.45 - up * 0.15;
      body.scale.set(1 + squash * 0.12, 1 - squash * 0.15 - slump * 0.06, 1 + squash * 0.12);
    },
  };
  g.userData.pose();
  return g;
}

// ---------------------------------------------------------------- 画布贴图文字（多层叠出厚度的“立体字”）
function word3d(text, { color = '#2E5E8C', side = '#173452', size = 1.0, font = '900 220px NotoSerifSC', layers = 9 } = {}) {
  const cvw = Math.max(512, text.length * 240 + 80), cvh = 300;
  const tex = (fill, stroke) => canvasTex(cvw, cvh, (g, w, h) => {
    g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle';
    if (stroke) { g.lineWidth = 22; g.lineJoin = 'round'; g.strokeStyle = stroke; g.strokeText(text, w / 2, h / 2 + 8); }
    g.fillStyle = fill; g.fillText(text, w / 2, h / 2 + 8);
  });
  const front = tex(color, '#FFFFFF'), back = tex(side, side);
  const g = new THREE.Group();
  const pw = cvw / 300 * size, ph = size;
  for (let i = 0; i < layers; i++) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(pw, ph), new THREE.MeshBasicMaterial({
      map: i === layers - 1 ? front : back, transparent: true, alphaTest: 0.35, depthWrite: true, side: THREE.DoubleSide }));
    m.position.z = i * 0.025 * size;
    g.add(m);
  }
  g.userData.width = pw;
  return g;
}

function bubble(text) {
  const t = canvasTex(900, 300, (g, w, h) => {
    g.fillStyle = '#FFFFFF'; g.strokeStyle = '#2B2F3A'; g.lineWidth = 10;
    g.beginPath(); g.roundRect(20, 20, w - 40, h - 90, 60); g.fill(); g.stroke();
    g.beginPath(); g.moveTo(w / 2 - 40, h - 72); g.lineTo(w / 2, h - 18); g.lineTo(w / 2 + 40, h - 72); g.closePath(); g.fill();
    g.stroke(); g.fillStyle = '#FFFFFF'; g.fillRect(w / 2 - 34, h - 78, 68, 12);
    g.font = '900 104px NotoSansSC'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillStyle = '#2B2F3A'; g.fillText(text, w / 2, (h - 70) / 2 + 12);
  });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 0.8), new THREE.MeshBasicMaterial({ map: t, transparent: true }));
  return m;
}

// ---------------------------------------------------------------- 场景
function build() {
  const scene = new THREE.Scene();
  const hemi = new THREE.HemisphereLight('#FFF6E8', '#B9A58C', 1.15);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight('#FFE9C8', 2.1);
  sun.position.set(5, 10, 6);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8, near: 1, far: 30 });
  sun.shadow.bias = -0.0006;
  scene.add(sun);
  // 漂浮小岛：泥土侧面 + 木地板顶面
  const island = new THREE.Group();
  const soil = cyl(5.2, 4.2, 1.2, clay('#B98A5E', 0.95), 64);
  soil.position.y = -0.6;
  island.add(soil);
  const rock = cyl(4.2, 1.2, 1.8, clay('#9C7350', 0.95), 12);
  rock.position.y = -2.1;
  island.add(rock);
  const grass = cyl(5.25, 5.25, 0.12, clay('#9CC08A', 0.9), 64);
  grass.position.y = 0.0;
  island.add(grass);
  const floor = box(7.0, 0.1, 4.6, clay('#E8D3B0', 0.8), 0.05);
  floor.position.set(0, 0.1, -0.4);
  island.add(floor);
  for (let i = -3; i <= 3; i++) {
    const seam = box(0.02, 0.012, 4.5, clay('#D2B88E', 0.8), 0, { cast: false });
    seam.position.set(i, 0.156, -0.4);
    island.add(seam);
  }
  // 后墙 + 挂钟
  const wall = box(7.0, 2.6, 0.2, clay('#F4EDE2', 0.9), 0.06);
  wall.position.set(0, 1.4, -2.7);
  island.add(wall);
  const clock = wallClock(0.42);
  clock.position.set(0, 2.05, -2.57);
  island.add(clock);
  // 小树与花盆
  for (const [x, z, s] of [[-4.2, 1.6, 1], [4.3, -1.2, 0.8], [-3.6, -2.4, 0.9]]) {
    const pot = cyl(0.22 * s, 0.17 * s, 0.32 * s, clay('#C8664A', 0.8));
    pot.position.set(x, 0.22, z);
    const crown = sphere(0.5 * s, clay('#6FA36B', 0.9));
    crown.position.set(x, 0.85 * s + 0.2, z);
    island.add(pot, crown);
  }
  scene.add(island);
  // 工位
  const desks = [];
  for (const x of [-2.2, 0, 2.2]) {
    const d = new THREE.Group();
    const top = box(1.5, 0.08, 0.8, clay('#A87850', 0.7), 0.03);
    top.position.y = 0.78;
    d.add(top);
    for (const sx of [-0.65, 0.65]) for (const sz of [-0.3, 0.3]) {
      const leg = box(0.06, 0.74, 0.06, clay('#6E5038', 0.7));
      leg.position.set(sx, 0.4, sz);
      d.add(leg);
    }
    const mon = box(0.8, 0.5, 0.05, clay('#2B2F3A', 0.5), 0.03);
    mon.position.set(0, 1.15, -0.2);
    const screen = box(0.72, 0.42, 0.01, new THREE.MeshStandardMaterial({ color: '#7FC4E8', emissive: '#3A7FA8', emissiveIntensity: 0.6 }));
    screen.position.set(0, 1.15, -0.17);
    const stand = box(0.06, 0.2, 0.06, clay('#2B2F3A', 0.5));
    stand.position.set(0, 0.9, -0.2);
    d.add(mon, screen, stand);
    d.position.set(x, 0.15, -1.3);
    scene.add(d);
    desks.push(d);
  }
  const oldC = ['#4E86C4', '#E58C9A', '#7FB06A'], newC = ['#E8A24A', '#9A7CC8', '#4FB3A6'];
  const olds = oldC.map((c, i) => chibi(c, { long: i === 1, hair: i === 1 ? '#5A3A2A' : '#2A2420' }));
  const news = newC.map((c, i) => chibi(c, { long: i === 2, hair: i === 0 ? '#3A2A20' : '#1E1E24' }));
  [...olds, ...news].forEach(p => scene.add(p));
  const boss = chibi('#2F3442', { suit: true, pants: '#262A35', hair: '#3A3A44' });
  scene.add(boss);
  const say = bubble('咱们重新出发！');
  scene.add(say);
  // 彩纸
  const confetti = [];
  const cols = ['#F25C78', '#FFC93C', '#3CC6A8', '#4CB4F0', '#A889F0'];
  for (let i = 0; i < 70; i++) {
    const p = box(0.08, 0.02, 0.05, clay(cols[i % 5], 0.6), 0, { cast: false });
    p.userData = { a: (i * 2.399) % (Math.PI * 2), r: 1.5 + (i * 37 % 100) / 40, v: 3 + (i * 13 % 10) / 3, spin: (i % 7) - 3 };
    scene.add(p);
    confetti.push(p);
  }
  // 大书本 + 手 + 弹簧（放在岛前右侧）
  const book = new THREE.Group();
  for (const s of [-1, 1]) {
    const page = box(1.1, 0.08, 1.5, clay('#FBF6EA', 0.9), 0.03);
    page.position.set(s * 0.56, 0, 0);
    page.rotation.z = -s * 0.06;
    book.add(page);
    const cover = box(1.16, 0.06, 1.56, clay('#2E6E8C', 0.8), 0.03);
    cover.position.set(s * 0.58, -0.07, 0);
    cover.rotation.z = -s * 0.06;
    book.add(cover);
    for (let l = 0; l < 6; l++) {
      const line = box(0.8, 0.005, 0.03, clay('#C9C2B4', 0.9), 0, { cast: false });
      line.position.set(s * 0.56, 0.05, -0.5 + l * 0.2);
      book.add(line);
    }
  }
  book.position.set(2.7, 0.3, 1.9);
  book.rotation.y = -0.35;
  scene.add(book);
  const spring = new THREE.Group();
  const rings = [];
  for (let i = 0; i < 18; i++) {
    const r = torus(0.28, 0.035, clay(i % 2 ? '#C0C6CE' : '#A8B0BA', 0.35, { metalness: 0.6 }));
    r.rotation.x = Math.PI / 2;
    spring.add(r);
    rings.push(r);
  }
  scene.add(spring);
  const hand = new THREE.Group();
  const palm = mesh(new THREE.CapsuleGeometry(0.16, 0.16, 6, 14), clay('#F2CDA8', 0.75));
  palm.rotation.z = Math.PI / 2;
  const sleeve = cyl(0.17, 0.17, 1.6, clay('#4E86C4', 0.85));
  sleeve.position.y = 0.95;
  hand.add(palm, sleeve);
  scene.add(hand);
  // 立体字
  const W1 = word3d('不是人的问题', { color: '#2E5E8C', side: '#1A3550', size: 1.25 });
  const W2 = word3d('是结构', { color: '#E2701D', side: '#8A3E10', size: 1.7 });
  const quote = ['行为', '藏在', '结构', '里'].map((s, i) => word3d(s, i === 2
    ? { color: '#E2701D', side: '#8A3E10', size: 1.25 } : { color: '#2E5E8C', side: '#1A3550', size: 1.0 }));
  scene.add(W1, W2, ...quote);
  const glow = new THREE.PointLight('#FFB060', 0, 6);
  scene.add(glow);
  const camera = makeCamera(38);
  return { scene, camera, hemi, sun, olds, news, boss, say, confetti, book, spring, rings, hand, W1, W2, quote, clock, glow };
}

// ---------------------------------------------------------------- 相机：时间关键帧上的 Catmull-Rom 平滑路径
function camPath(keys) {
  const ts = keys.map(k => k[0]);
  const P = new THREE.CatmullRomCurve3(keys.map(k => new THREE.Vector3(...k[1])), false, 'centripetal');
  const L = new THREE.CatmullRomCurve3(keys.map(k => new THREE.Vector3(...k[2])), false, 'centripetal');
  return t => {
    let i = 0;
    while (i < ts.length - 2 && t > ts[i + 1]) i++;
    const k = easeInOut(clamp01((t - ts[i]) / (ts[i + 1] - ts[i])));
    const u = (i + k) / (ts.length - 1);
    return [P.getPoint(u), L.getPoint(u)];
  };
}

let S = null, cam = null;

function update(t) {
  const s = S;
  // ---- 相机
  const [pos, look] = cam(t);
  s.camera.position.copy(pos);
  s.camera.lookAt(look);
  // ---- 灯光：三个月后由暖转冷，drop 时回暖
  const cold = prog(t, B(3, 0), B(3, 3) - B(3, 0)) * (1 - prog(t, B(4, 0), 0.4));
  s.hemi.color.set('#FFF6E8').lerp(new THREE.Color('#BFD3F0'), cold);
  s.sun.color.set('#FFE9C8').lerp(new THREE.Color('#9FB8E0'), cold);
  s.sun.intensity = lerp(2.1, 1.3, cold);
  // ---- 领导：小节 0 从右侧走到中前方，第 1 拍开口
  const walkK = prog(t, 0, B(0, 1) - 0.05);
  const bx = lerp(4.6, 0.9, easeOut(walkK)), bz = lerp(1.2, 0.9, walkK);
  s.boss.position.set(bx, 0.15, bz);
  s.boss.rotation.y = lerp(-1.2, -0.25, easeOut(walkK));
  s.boss.userData.pose({ walk: walkK * 6, amp: walkK < 1 ? 0.8 : 0, wave: easeOut(prog(t, B(0, 1), 0.3)) * (t < B(4, 0) ? 1 : 0),
    squash: pulse(t, B(0, 1), 8, 16) * 0.6 });
  const sayK = easeOutBack(prog(t, B(0, 1), 0.35)) * (1 - prog(t, B(1, 0) + 0.2, 0.3));
  s.say.visible = sayK > 0.01;
  s.say.position.set(bx + 0.4, 2.35, bz + 0.2);
  s.say.scale.setScalar(Math.max(0.001, sayK));
  s.say.quaternion.copy(s.camera.quaternion);
  if (t > B(4, 0)) s.boss.visible = false; else s.boss.visible = true;
  // ---- 工位上的人：小节 1 三个拍点依次替换；小节 2 跳起欢呼；小节 3 垂头
  for (let i = 0; i < 3; i++) {
    const x = [-2.2, 0, 2.2][i];
    const tSwap = B(1, i);
    const outK = easeIn(prog(t, tSwap, 0.2));
    const inK = easeOutBack(prog(t, tSwap + 0.12, 0.35), 2.2);
    const o = s.olds[i], n = s.news[i];
    o.position.set(x, 0.15 - outK * 1.2, -0.55);
    o.scale.setScalar(Math.max(0.001, 1 - outK));
    o.visible = outK < 1;
    o.userData.pose({});
    const jumpT = [B(2, 0), B(2, 1), B(2, 2)][i];
    const j = t >= B(2, 0) && t < B(3, 0) ? Math.max(0, Math.sin(clamp01((t - jumpT) / 0.5) * Math.PI)) * 0.55 : 0;
    const cheer = easeOut(prog(t, jumpT, 0.2)) * (1 - prog(t, B(3, 0), 0.3));
    const slump = easeInOut(prog(t, B(3, 1), 0.8)) * (1 - prog(t, B(4, 0), 0.3));
    n.position.set(x, 0.15 + (1 - inK) * 0.0, -0.55);
    n.scale.setScalar(Math.max(0.001, inK));
    n.visible = inK > 0.001;
    n.userData.pose({ up: cheer, jump: j, slump, squash: pulse(t, tSwap + 0.12, 7, 15) * 0.5 });
    n.rotation.y = 0;
  }
  // ---- 彩纸：小节 2 第 3 拍
  const ct = t - B(2, 3);
  s.confetti.forEach((p, i) => {
    const d = p.userData;
    p.visible = ct > 0 && ct < 2.2;
    if (!p.visible) return;
    p.position.set(Math.cos(d.a) * d.r * ct * 0.8, 2.2 + d.v * ct - 4.9 * ct * ct * 0.55, -0.6 + Math.sin(d.a) * d.r * ct * 0.5);
    p.rotation.set(ct * d.spin, ct * d.spin * 0.7, ct * 2);
  });
  // ---- 挂钟：小节 3 指针飞转三圈多
  const hours = 9 + easeInOut(prog(t, B(3, 0), B(3, 3) - B(3, 0) + 0.3)) * 36 * 3;
  s.clock.userData.set(hours);
  s.clock.scale.setScalar(1 + bump(t, B(3, 0), 6) * 0.25 + bump(t, B(3, 2), 8) * 0.12);
  // ---- drop 立体字：第 0 拍、第 1 拍砸下，小节 5 开始飞走
  const leave = easeIn(prog(t, B(5, 0) - 0.1, 0.45));
  const slam = (g, tb, y, z) => {
    const k = prog(t, tb - 0.22, 0.22);
    g.visible = t > tb - 0.22 && leave < 1;
    g.position.set(0, lerp(y + 6, y, easeIn(k)) + leave * 8, z);
    const sq = pulse(t, tb, 7, 20);
    g.scale.set(1 + sq * 0.18, 1 - sq * 0.22, 1);
  };
  slam(s.W1, B(4, 0), 4.6, 0.6);
  slam(s.W2, B(4, 1), 3.0, 0.9);
  // ---- 弹簧：小节 5 手提起（第 0 拍），小节 6 第 1 拍松手后自己上下弹
  const bookX = 2.7, bookY = 0.42, bookZ = 1.9;
  const liftK = easeOut(prog(t, B(5, 0), 0.45));
  const rel = t - B(6, 1);
  let topY, len;
  if (rel < 0) {
    topY = bookY + 0.2 + liftK * 1.5;
    len = lerp(0.35, 1.25, liftK);
  } else {
    const osc = Math.cos(rel * 9.5) * Math.exp(-rel * 1.6);
    len = 0.75 + 0.5 * osc;
    topY = bookY + len + 0.08 + 0.15 * Math.max(0, osc);
  }
  s.spring.visible = t > B(5, 0) - 0.4;
  s.rings.forEach((r, i) => {
    r.position.set(bookX, topY - len * (i / (s.rings.length - 1)), bookZ);
  });
  s.spring.scale.setScalar(1);
  const handUp = rel < 0 ? 0 : easeOut(clamp01(rel / 0.4)) * 2.2;
  s.hand.visible = s.spring.visible && handUp < 2.1;
  s.hand.position.set(bookX, topY + 0.15 + handUp, bookZ);
  s.hand.scale.setScalar(easeOutBack(prog(t, B(5, 0) - 0.35, 0.35)));
  // ---- 金句：小节 7 逐词弹出
  const qx = [-2.6, -0.9, 1.0, 2.6], qy = [4.2, 4.2, 4.0, 4.2];
  s.quote.forEach((g, i) => {
    const k = easeOutBack(prog(t, B(7, i), 0.35), 2.4);
    g.visible = k > 0.001;
    g.scale.setScalar(Math.max(0.001, k) * (1 + bump(t, B(7, i), 7) * 0.15));
    g.position.set(qx[i], qy[i] + (1 - k) * -1.2, 1.0);
  });
  s.glow.intensity = t > B(7, 2) ? 12 * (0.6 + 0.4 * bump(t, B(7, 2), 3)) : 0;
  s.glow.position.set(1.0, 4.0, 2.2);
}

// ---------------------------------------------------------------- UI：页眉 + 底部字幕
const ui = document.getElementById('ui');
function el(css, html = '') {
  const e = document.createElement('div');
  Object.assign(e.style, { position: 'absolute', ...css });
  e.innerHTML = html;
  ui.appendChild(e);
  return e;
}
const head1 = el({ left: '64px', top: '150px', font: '500 32px NotoSansSC', color: '#5B6470' }, '系统之美 · 10讲');
const head2 = el({ left: '64px', top: '196px', font: '900 58px NotoSansSC', color: '#2B2F3A' }, '01 系统是什么');
const cap = el({ left: '540px', top: '1440px', textAlign: 'center', font: '900 66px NotoSansSC', whiteSpace: 'nowrap',
  color: '#2B2F3A', lineHeight: '92px', padding: '16px 52px', borderRadius: '34px', background: 'rgba(255,255,255,0.9)',
  boxShadow: '0 10px 30px rgba(40,30,20,0.16)' });

function drawUI(t) {
  const bar = TLD.bars.find(b => t < b.t1) || TLD.bars[TLD.bars.length - 1];
  const a = clamp01((t - 0.2) / 0.5);
  head1.style.opacity = a; head2.style.opacity = a;
  if (cap._t !== bar.text) { cap.textContent = bar.text; cap._t = bar.text; }
  const k = easeOut(prog(t, bar.t0, 0.3));
  cap.style.opacity = String(k);
  cap.style.transform = `translateX(-50%) translateY(${(1 - k) * 22}px)`;
}

function paintBackground() {
  const g = document.getElementById('bg').getContext('2d');
  const lin = g.createLinearGradient(0, 0, 0, H);
  lin.addColorStop(0, '#FCEBD6');
  lin.addColorStop(0.55, '#F3E6EE');
  lin.addColorStop(1, '#D9E6F4');
  g.fillStyle = lin; g.fillRect(0, 0, W, H);
  for (const [x, y, r] of [[200, 420, 70], [270, 400, 90], [350, 430, 60], [820, 1180, 80], [900, 1150, 100], [980, 1190, 70]]) {
    g.fillStyle = 'rgba(255,255,255,0.75)';
    g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
  }
}

const fx = document.getElementById('fx').getContext('2d');
function drawFX(t) {
  fx.clearRect(0, 0, W, H);
  let a = Math.max(1 - clamp01(t / 0.35), clamp01((t - (TLD.end - 0.5)) / 0.5));
  // drop 两记重击闪白
  for (const tb of [B(4, 0), B(4, 1)]) if (t >= tb) a = Math.max(a, 0.55 * Math.exp(-(t - tb) * 10));
  if (a > 0) { fx.fillStyle = `rgba(255,250,240,${a})`; fx.fillRect(0, 0, W, H); }
}

let renderer = null;
async function boot() {
  TLD = await (await fetch('./timeline.json')).json();
  paintBackground();
  renderer = initRenderer(document.getElementById('gl'));
  for (const f of ['500 32px NotoSansSC', '900 32px NotoSansSC', '900 32px NotoSerifSC']) await document.fonts.load(f);
  S = build();
  cam = camPath([
    [0.0, [6.5, 5.2, 9.5], [0.6, 1.0, -0.3]],
    [B(1, 0), [3.2, 3.4, 6.6], [0, 1.1, -0.8]],
    [B(2, 0), [-2.8, 3.1, 6.0], [0, 1.3, -0.8]],
    [B(3, 0), [-0.6, 2.8, 4.6], [0, 1.9, -2.2]],
    [B(4, 0) - 0.05, [0.2, 3.0, 5.2], [0, 2.0, -1.5]],
    [B(4, 0) + 0.45, [0.0, 7.2, 15.5], [0, 3.2, 0]],
    [B(5, 0) + 0.2, [5.4, 2.9, 6.0], [2.7, 1.4, 1.9]],
    [B(6, 1), [4.6, 2.5, 5.0], [2.7, 1.25, 1.9]],
    [B(7, 0), [2.0, 4.6, 10.5], [0.2, 3.4, 0.6]],
    [TLD.end, [-1.6, 4.8, 10.8], [0.2, 3.4, 0.6]],
  ]);
  renderer.compile(S.scene, S.camera);
  window.AC.ready = true;
}

window.AC = {
  ready: false,
  seek(t) {
    update(t);
    renderer.render(S.scene, S.camera);
    drawUI(t);
    drawFX(t);
    return 0;
  },
  info() { return { end: TLD.end }; },
};

boot().catch(e => { window.AC.error = String(e && e.stack || e); console.error(e); });
