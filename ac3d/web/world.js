// 漏船世界：全片贯穿的比喻。房子 = 浮在橙色“热潮”上的漏船；水位 = 温度；板缝渗水 = 墙体渗热（快慢 ∝ 内外水位差）；
// 空调 = 往外车水的龙骨水车；每车出一斗落一枚铜钱 = 电费。所有状态由 set(...) 显式设置，镜头按时间算好后传入。
import {
  THREE, PAL, box, cyl, sphere, torus, mesh, group, at, clay, lacquer, metal, glow, canvasTex, rng, clamp01, lerp,
} from './engine.js';
import { coinStack, shadeHex, acIndoor } from './props.js';

export const SEA = '#E8813F';

// ---------------------------------------------------------------- 热潮水面（原点：水面中心；userData.set(水位 y, t)）
export function heatSea({ size = 90, opacity = 0.86 } = {}) {
  const g = new THREE.Group();
  const tex = canvasTex(1024, 1024, (c) => {
    c.fillStyle = 'rgba(255,255,255,0)'; c.fillRect(0, 0, 1024, 1024);
    c.strokeStyle = 'rgba(90,40,20,0.55)'; c.lineWidth = 3;
    const r = rng(41);
    for (let i = 0; i < 60; i++) {                        // 墨线水纹
      const x = r() * 1024, y = r() * 1024, w = 40 + r() * 120;
      c.beginPath();
      c.moveTo(x, y);
      c.bezierCurveTo(x + w * 0.3, y - 14, x + w * 0.7, y - 14, x + w, y);
      c.stroke();
    }
  });
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(9, 9);
  const water = new THREE.Mesh(new THREE.PlaneGeometry(size, size, 1, 1), new THREE.MeshStandardMaterial({
    color: '#EE9555', transparent: true, opacity, roughness: 0.35, metalness: 0.0, emissive: '#B8461C', emissiveIntensity: 0.2,
    depthWrite: false }));
  water.rotation.x = -Math.PI / 2;
  water.receiveShadow = true;
  const lines = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshBasicMaterial({ map: tex, transparent: true,
    depthWrite: false, opacity: 0.6 }));
  lines.rotation.x = -Math.PI / 2;
  lines.position.y = 0.01;
  g.add(water, lines);
  g.userData = {
    water, lines,
    set(y, t) {
      g.position.y = y;
      tex.offset.set((t * 0.02) % 1, (t * 0.035) % 1);
    },
  };
  return g;
}

// ---------------------------------------------------------------- 竹标水位计（原点：竹竿底；userData.set(水位世界 y)）
export function levelPole({ h = 5, color = PAL.cinnabar } = {}) {
  const g = new THREE.Group();
  const rod = cyl(0.07, 0.08, h, clay(PAL.bamboo, 0.6), 14);
  rod.position.y = h / 2;
  g.add(rod);
  for (let i = 1; i < 5; i++) {
    const n = torus(0.085, 0.022, clay(shadeHex(PAL.bamboo, 0.7), 0.6));
    n.rotation.x = Math.PI / 2;
    n.position.y = h * i / 5;
    g.add(n);
  }
  const cap = cyl(0.11, 0.11, 0.12, metal('#C8A15E', 0.4), 16);
  cap.position.y = h;
  g.add(cap);
  const bead = sphere(0.26, lacquer(color, 0.4));
  g.add(bead);
  const tassel = new THREE.Group();
  for (let i = 0; i < 7; i++) {
    const s = cyl(0.012, 0.012, 0.5, clay(color, 0.8), 5, { cast: false });
    s.position.set((i - 3) * 0.03, -0.4, 0);
    tassel.add(s);
  }
  bead.add(tassel);
  g.userData = {
    bead, tassel,
    /** 把红珠放到世界坐标水位 y；swing 为穗子甩动角 */
    set(levelWorldY, swing = 0) {
      g.updateWorldMatrix(true, false);
      const baseY = g.getWorldPosition(new THREE.Vector3()).y;
      bead.position.y = clamp01((levelWorldY - baseY) / h) * h;
      tassel.rotation.z = swing;
    },
  };
  return g;
}

// ---------------------------------------------------------------- 剖面漏船（鱼缸剖面：船长沿 -z，在 z=0 处横切，正面露出截面）
// 局部坐标：船宽沿 x（±B/2），船底 y=bottom，船帮 y=top；船外热潮截面在船两侧与船底下方，水位由 set({outer}) 控制。
const cutMat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.4, transparent: true, opacity: 0.88,
  emissive: '#C04A1A', emissiveIntensity: 0.22, depthWrite: true, ...extra });

export function cutBoat({ B = 4.0, L = 7.5, bottom = -2.5, top = 0.7, planks = 5, sea = true, seaW = 9, floor = -4.2,
  ac = true, roof = true, sail = null } = {}) {
  const g = new THREE.Group();
  const D = top - bottom;
  const ph = D / planks, gap = 0.07, th = 0.24;
  const plankMats = [];
  const seams = [];
  for (const side of [-1, 1]) {
    for (let k = 0; k < planks; k++) {
      const m = new THREE.MeshStandardMaterial({ color: k % 2 ? '#6E4128' : '#7C4B2F', roughness: 0.7, emissive: '#FF7A2E', emissiveIntensity: 0 });
      plankMats.push(m);
      const p = mesh(new THREE.BoxGeometry(th, ph - gap, L), m);
      p.position.set(side * (B / 2 - th / 2 + 0.02 * (planks - k)), bottom + ph * (k + 0.5), -L / 2);
      g.add(p);
      if (k > 0) seams.push({ x: side * (B / 2 + 0.05), y: bottom + ph * k, side });
    }
    const rail = box(th * 1.6, 0.16, L + 0.2, clay(PAL.wood, 0.6), 0.04);
    rail.position.set(side * (B / 2 - th / 2), top + 0.06, -L / 2);
    g.add(rail);
  }
  const bot = box(B, 0.26, L, clay('#5E3A24', 0.75));
  bot.position.set(0, bottom - 0.13, -L / 2);
  g.add(bot);
  const stern = box(B, D, 0.24, clay('#6E4128', 0.7));
  stern.position.set(0, bottom + D / 2, -L);
  g.add(stern);
  // 船内的水（室内温度）：截面在 z=0
  const coolC = new THREE.Color('#F7DCB8'), hotC = new THREE.Color('#FF8F45');
  const innerM = cutMat('#F7DCB8', { emissiveIntensity: 0.05 });
  const innerMesh = mesh(new THREE.BoxGeometry(B - 2 * th - 0.04, 1, L - 0.3), innerM, { cast: false });
  g.add(innerMesh);
  const innerLine = box(B - 2 * th - 0.04, 0.05, 0.05, clay(PAL.ink, 0.8), 0, { cast: false });
  g.add(innerLine);
  // 船外热潮截面：左右两块 + 船底下方一块（截面在 z=0），再往后是延伸到天边的水面
  const seaParts = [], seaLines = [];
  if (sea) {
    const sm = cutMat('#EE8C4C');
    const mk = (w, x, dz = 34, zc = -17) => { const m = mesh(new THREE.BoxGeometry(w, 1, dz), sm, { cast: false }); m.userData.x = x; m.userData.z = zc; g.add(m); seaParts.push(m); return m; };
    mk(seaW, -(B / 2 + seaW / 2));
    mk(seaW, B / 2 + seaW / 2);
    mk(B, 0, 34 - L - 0.12, -(34 + L + 0.12) / 2);
    const under = mesh(new THREE.BoxGeometry(B, bottom - 0.26 - floor, 34), sm, { cast: false });
    under.position.set(0, (bottom - 0.26 + floor) / 2, -17);
    g.add(under);
    for (const side of [-1, 1]) {
      const ln = box(seaW, 0.05, 0.05, clay(PAL.ink, 0.8), 0, { cast: false });
      ln.position.x = side * (B / 2 + seaW / 2);
      g.add(ln);
      seaLines.push(ln);
    }
    const bed = box(B + 2 * seaW, 0.3, 34, clay('#7A5A3E', 0.9));
    bed.position.set(0, floor - 0.15, -17);
    g.add(bed);
  }
  // 屋子身份：船尾两根朱柱、横梁上挂空调；可选抬起的瓦顶
  let acU = null, roofG = null;
  for (const side of [-1, 1]) {
    const col = cyl(0.12, 0.14, 2.6, lacquer(PAL.rouge, 0.5), 18);
    col.position.set(side * (B / 2 - 0.25), top + 1.3, -L + 0.3);
    g.add(col);
  }
  const beam = box(B, 0.18, 0.2, clay(PAL.wood, 0.6), 0.04);
  beam.position.set(0, top + 2.5, -L + 0.3);
  g.add(beam);
  if (ac) {
    acU = acIndoor({ w: 2.0, h: 0.6, d: 0.46 });
    acU.position.set(0, top + 1.9, -L + 0.6);
    g.add(acU);
  }
  if (roof) {
    roofG = new THREE.Group();
    for (const sgn of [-1, 1]) {
      const panel = box(B * 0.66, 0.16, 2.6, clay(PAL.tile, 0.75), 0.05);
      panel.rotation.z = sgn * 0.45;
      panel.position.set(sgn * B * 0.27, 0, -L + 0.6);
      roofG.add(panel);
    }
    const ridge = box(0.28, 0.24, 2.9, clay(shadeHex(PAL.tile, 0.7), 0.7), 0.06);
    ridge.position.set(0, 0.28, -L + 0.6);
    roofG.add(ridge);
    roofG.position.y = top + 3.0;
    g.add(roofG);
  }
  let sailM = null;
  if (sail) {
    const tex = canvasTex(256, 512, (c) => {
      c.fillStyle = '#F2E6CC'; c.fillRect(0, 0, 256, 512);
      c.strokeStyle = '#B88A4A'; c.lineWidth = 8; c.strokeRect(10, 10, 236, 492);
      const chars = [...sail];
      const step = Math.min(110, 440 / chars.length);
      c.fillStyle = PAL.ink; c.font = `900 ${Math.round(step * 0.86)}px "NotoSerifSC"`; c.textAlign = 'center'; c.textBaseline = 'middle';
      chars.forEach((ch, i) => c.fillText(ch, 128, 256 + (i - (chars.length - 1) / 2) * step));
    });
    const mast = cyl(0.06, 0.07, 4.2, clay(PAL.wood, 0.6), 12);
    mast.position.set(-B / 2 + 0.6, top + 2.1, -L * 0.5);
    g.add(mast);
    sailM = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 2.6), new THREE.MeshStandardMaterial({ map: tex, side: THREE.DoubleSide, roughness: 0.9 }));
    sailM.position.set(-B / 2 + 1.3, top + 2.5, -L * 0.5);
    sailM.castShadow = true;
    g.add(sailM);
  }
  g.userData = {
    B, L, bottom, top, seams, roof: roofG, ac: acU, sail: sailM, plankMats, innerM,
    /** outer/inner：船外、船内水位（局部 y）；soak：船板吸热发光；warm：船内水温 0–1（缺省按水位估） */
    set({ outer = 0, inner = -1.5, soak = 0, warm = null } = {}) {
      const ih = Math.max(0.02, inner - bottom);
      innerMesh.scale.y = ih;
      innerMesh.position.set(0, bottom + ih / 2, -(L - 0.3) / 2);
      innerLine.position.set(0, inner, 0.02);
      const w = warm === null ? clamp01((inner - bottom - 0.6) / (D - 0.6)) : clamp01(warm);
      innerM.color.copy(coolC).lerp(hotC, w);
      innerM.emissiveIntensity = 0.05 + 0.4 * w;
      const oh = Math.max(0.02, outer - floor);
      seaParts.forEach(m => { m.scale.y = oh; m.position.set(m.userData.x, floor + oh / 2, m.userData.z); });
      seaLines.forEach(l => { l.position.y = outer; l.position.z = 0.02; });
      plankMats.forEach((m, i) => { m.emissiveIntensity = 0.5 * clamp01(soak * 1.6 - (i % 5) * 0.12); });
    },
  };
  g.userData.set({});
  return g;
}

// ---------------------------------------------------------------- 板缝射流（从船外横穿板缝射进船舱，落到船内水面）
export function cutJets(boat, { n = 320, seed = 5 } = {}) {
  const geo = new THREE.SphereGeometry(0.085, 10, 6);
  const inst = new THREE.InstancedMesh(geo, glow('#FF7A2E', 1.0), n);
  const R = rng(seed);
  const seeds = Array.from({ length: n }, () => [R(), R(), R(), R()]);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(), p = new THREE.Vector3();
  inst.userData = {
    /** strength：射流强度 0–1（∝ 水位差）；outer/inner：船外、船内水位（局部 y）；只有低于船外水位的缝会进水 */
    update(t, strength, outer, inner) {
      const { seams, L } = boat.userData;
      for (let i = 0; i < n; i++) {
        const [a, b, c, d] = seeds[i];
        const s = seams[Math.floor(a * seams.length)];
        const live = s.y < outer - 0.05 && strength > 0.02 && b < 0.2 + 0.8 * strength;
        const u = (t * (0.5 + 1.4 * strength) * (0.75 + 0.5 * d) + c) % 1;
        const reach = 0.5 + 1.3 * strength;
        const y0 = s.y;
        let y = y0 - u * u * (y0 - inner + 0.2) * 0.9;
        if (y < inner) y = inner;
        p.set(s.x - s.side * (0.3 + u * reach), y, -0.25 - d * (L - 0.6) * (c < 0.5 ? 0.25 : 1));
        const k = live ? (0.55 + 0.8 * strength) * Math.min(1, Math.sin(Math.PI * u) * 1.6) + 0.02 : 0.0001;
        sc.set(k, k, k);
        m4.compose(p, q, sc);
        inst.setMatrixAt(i, m4);
      }
      inst.instanceMatrix.needsUpdate = true;
    },
  };
  boat.add(inst);
  return inst;
}

// ---------------------------------------------------------------- 龙骨水车（原点：木槽下端；沿 +x 斜向上；update(t, 链条位移, 倾泻强度)）
export function dragonWheel({ len = 5.0, angle = 0.8, paddles = 16 } = {}) {
  const g = new THREE.Group();
  const trough = new THREE.Group();
  const base = box(len, 0.1, 0.6, clay(PAL.wood2, 0.7), 0.03);
  const wallA = box(len, 0.4, 0.08, clay(PAL.wood2, 0.7), 0.02);
  wallA.position.set(0, 0.2, 0.3);
  const wallB = wallA.clone();
  wallB.position.z = -0.3;
  trough.add(base, wallA, wallB);
  trough.position.x = len / 2;
  const arm = new THREE.Group();
  arm.rotation.z = angle;
  arm.add(trough);
  g.add(arm);
  // 顶端大轮（辐条）与下端小轴
  const wheel = new THREE.Group();
  const rim = torus(0.75, 0.07, clay(PAL.wood, 0.6));
  wheel.add(rim);
  for (let i = 0; i < 8; i++) {
    const sp = box(1.5, 0.07, 0.07, clay(PAL.wood, 0.6));
    sp.rotation.z = i * Math.PI / 8;
    wheel.add(sp);
  }
  const hub = cyl(0.16, 0.16, 0.7, clay(PAL.wood, 0.6), 16);
  hub.rotation.x = Math.PI / 2;
  wheel.add(hub);
  wheel.position.set(len, 0.2, 0);
  arm.add(wheel);
  // 刮板链：沿“木槽上沿去、下沿回”的环路排布
  const loopLen = len * 2 + 1.2;
  const pads = [];
  for (let i = 0; i < paddles; i++) {
    const pad = box(0.08, 0.36, 0.5, clay('#8A5A3A', 0.6), 0.02);
    arm.add(pad);
    pads.push(pad);
  }
  // 倾泻水流：顶端出口向下的一道弧（挂在未旋转的外层，保证竖直下落）
  const ex = Math.cos(angle) * len, ey = Math.sin(angle) * len;
  const pourPts = [];
  for (let i = 0; i <= 10; i++) { const u = i / 10; pourPts.push(new THREE.Vector3(ex + 0.35 + u * 0.7, ey + 0.1 - u * u * 3.2, 0)); }
  const pour = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pourPts), 40, 0.15, 10, false),
    new THREE.MeshStandardMaterial({ color: '#FF9A55', transparent: true, opacity: 0.0, emissive: '#C8501E', emissiveIntensity: 0.45, depthWrite: false }));
  g.add(pour);
  g.userData = {
    arm, wheel, pads, pour,
    /** offset：链条走过的距离；flow：倾泻强度 0–1；blur：高速时刮板拉长（残影感） */
    update(offset, flow, blur = 0) {
      wheel.rotation.z = -offset / 0.75;
      pads.forEach((pad, i) => {
        let s = ((offset + i * loopLen / paddles) % loopLen + loopLen) % loopLen;
        if (s < len) { pad.position.set(s, 0.32, 0); pad.rotation.z = 0; }
        else if (s < len + 0.6) { const a = (s - len) / 0.6 * Math.PI; pad.position.set(len + Math.sin(a) * 0.5, 0.2 + Math.cos(a) * 0.4, 0); pad.rotation.z = -a; }
        else if (s < len * 2 + 0.6) { pad.position.set(len - (s - len - 0.6), -0.2, 0); pad.rotation.z = Math.PI; }
        else { const a = (s - len * 2 - 0.6) / 0.6 * Math.PI; pad.position.set(-Math.sin(a) * 0.5, -0.2 + Math.cos(Math.PI - a) * -0.4 + 0.0, 0); pad.rotation.z = Math.PI + a; }
        pad.scale.x = 1 + blur * 3;
      });
      pour.material.opacity = 0.8 * clamp01(flow);
      pour.visible = flow > 0.01;
    },
  };
  g.userData.update(0, 0);
  return g;
}

// ---------------------------------------------------------------- 浮石台 + 钱串柱（原点：石台顶面中心）
export function coinPier({ max = 34, seed = 3, ghost = false } = {}) {
  const g = new THREE.Group();
  const stone = mesh(new THREE.CylinderGeometry(0.95, 1.15, 1.4, 9), clay('#8E8A80', 0.9));
  stone.position.y = -0.7;
  g.add(stone);
  const stack = coinStack(max, { seed });
  g.add(stack);
  let ghostM = null;
  if (ghost) {
    ghostM = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 1, 40), new THREE.MeshStandardMaterial({ color: '#E2C27A',
      transparent: true, opacity: 0.28, roughness: 0.5, depthWrite: false }));
    g.add(ghostM);
  }
  g.userData = {
    stack,
    set(n, ghostN = 0) {
      stack.userData.set(n);
      if (ghostM) {
        const h = Math.max(0.01, ghostN * 0.13);
        ghostM.scale.y = h;
        ghostM.position.set(1.25, h / 2, 0);
        ghostM.visible = ghostN > 0.1;
      }
    },
  };
  return g;
}
