// 现代客厅剖面（无顶、前墙打开的“娃娃屋”视角）：后墙大窗、白色分体空调室内机、阳台上的室外机、
// 电视、挂钟、沙发、茶几、绿植、右墙门。原点在地面中心，x 向右、z 向前（镜头一侧），单位约为米。
import {
  THREE, box, cyl, sphere, torus, mesh, group, at, clay, metal, canvasTex, rng, clamp01, lerp, RoundedBoxGeometry,
} from './engine.js';

export const ROOM = { w: 6, d: 5, h: 3, wall: 0.25 };
export const MOD = {
  bg: '#EEF2F5', bg2: '#DCE4EB', ink: '#1F2A36', ink2: '#5B6875', ink3: '#93A0AC',
  cool: '#2F80ED', cool2: '#8EC5FF', heat: '#F2994A', heat2: '#FFC27A', hot: '#EB5757', ok: '#27AE60',
  wall: '#F4F1EB', cut: '#D5D0C6', floor: '#C8A47E', white: '#FAFAF8',
};

// 可单独调发光的材质（墙和家具“存热”辉光用，不走 clay 缓存）
function warmable(color, rough = 0.85) {
  return new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0, emissive: MOD.heat, emissiveIntensity: 0 });
}
const plastic = (c, r = 0.35) => new THREE.MeshPhysicalMaterial({ color: c, roughness: r, clearcoat: 0.6, clearcoatRoughness: 0.3 });

// ---------------------------------------------------------------- 空调室内机（原点：机身中心，正面朝 +z）
export function acIndoor() {
  const g = new THREE.Group();
  const W = 1.3, Hh = 0.36, D = 0.26;
  g.add(box(W, Hh, D, plastic('#FBFBF9'), 0.08));
  const lower = box(W * 0.98, 0.1, D * 0.9, plastic('#ECEDEB', 0.4), 0.04, { cast: false });
  lower.position.set(0, -Hh / 2 + 0.06, 0.01);
  g.add(lower);
  const slot = box(W * 0.9, 0.05, 0.04, clay('#2A2F35', 0.9), 0.015, { cast: false });
  slot.position.set(0, -Hh / 2 + 0.03, D / 2 - 0.03);
  g.add(slot);
  const pivot = new THREE.Group();
  pivot.position.set(0, -Hh / 2 + 0.02, D / 2 - 0.01);
  const louver = box(W * 0.88, 0.02, 0.1, plastic('#F2F2F0'), 0.008);
  louver.position.z = 0.05;
  pivot.add(louver);
  g.add(pivot);
  const cv = document.createElement('canvas');
  cv.width = 256; cv.height = 112;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.2, 0.0875),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false }));
  screen.position.set(W * 0.33, 0.04, D / 2 + 0.003);
  g.add(screen);
  const led = sphere(0.012, new THREE.MeshBasicMaterial({ color: '#38D39F', toneMapped: false }), { cast: false });
  led.position.set(W * 0.43, -0.03, D / 2 + 0.004);
  g.add(led);
  let last = '';
  g.userData = {
    /** open：导风板开度 0–1；text：屏幕文字（空串熄屏）；on：指示灯 */
    set(open, text, on) {
      pivot.rotation.x = lerp(0, 1.05, clamp01(open));
      led.visible = !!on;
      const key = text + on;
      if (key === last) return;
      last = key;
      const c = cv.getContext('2d');
      c.clearRect(0, 0, 256, 112);
      if (text) {
        c.fillStyle = 'rgba(20,28,36,0.9)';
        c.beginPath(); c.roundRect(4, 4, 248, 104, 18); c.fill();
        c.fillStyle = '#6FE3FF';
        c.font = `700 ${text.length > 3 ? 54 : 78}px "NotoSansSC"`;
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText(text, 128, 60);
      }
      tex.needsUpdate = true;
    },
  };
  g.userData.set(1, '26°', true);
  return g;
}

// ---------------------------------------------------------------- 空调室外机（原点：底部中心，风扇朝 +z）
export function acOutdoor() {
  const g = new THREE.Group();
  const W = 0.86, Hh = 0.62, D = 0.32;
  const body = box(W, Hh, D, clay('#E3E5E6', 0.5), 0.03);
  body.position.y = Hh / 2;
  g.add(body);
  const cx = -0.12, cy = Hh / 2, R = 0.23;
  const hole = cyl(R, R, 0.02, clay('#30353A', 0.9), 48, { cast: false });
  hole.rotation.x = Math.PI / 2;
  hole.position.set(cx, cy, D / 2 + 0.002);
  g.add(hole);
  const fan = new THREE.Group();
  for (let i = 0; i < 3; i++) {
    const arm = new THREE.Group();
    const blade = box(0.11, 0.2, 0.01, clay('#8E959B', 0.6), 0.03, { cast: false });
    blade.position.y = 0.11;
    blade.rotation.y = 0.35;
    arm.rotation.z = i * Math.PI * 2 / 3;
    arm.add(blade);
    fan.add(arm);
  }
  fan.position.set(cx, cy, D / 2 + 0.015);
  g.add(fan);
  const grille = new THREE.Group();
  for (const r of [0.08, 0.15, 0.22]) grille.add(torus(r, 0.006, clay('#4A5056', 0.6)));
  for (let i = 0; i < 4; i++) {
    const bar = box(R * 2, 0.008, 0.008, clay('#4A5056', 0.6), 0, { cast: false });
    bar.rotation.z = i * Math.PI / 4;
    grille.add(bar);
  }
  grille.position.set(cx, cy, D / 2 + 0.03);
  g.add(grille);
  for (let i = 0; i < 9; i++) {                         // 右侧散热格栅
    const fin = box(0.24, 0.012, 0.01, clay('#BFC4C8', 0.6), 0, { cast: false });
    fin.position.set(0.27, 0.14 + i * 0.045, D / 2 + 0.006);
    g.add(fin);
  }
  for (const x of [-0.32, 0.32]) {                      // 支脚
    const foot = box(0.1, 0.04, D + 0.06, metal('#7A8188', 0.5), 0);
    foot.position.set(x, 0.02, 0);
    g.add(foot);
  }
  g.userData = { fan };
  return g;
}

// ---------------------------------------------------------------- 电视（原点：屏幕中心；画面是可重绘的画布）
export function tv() {
  const g = new THREE.Group();
  const W = 1.8, Hh = 1.0125;
  g.add(box(W + 0.05, Hh + 0.05, 0.05, clay('#15181B', 0.4), 0.01));
  const cv = document.createElement('canvas');
  cv.width = 1280; cv.height = 720;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(W, Hh), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }));
  scr.position.z = 0.027;
  g.add(scr);
  g.userData = { canvas: cv, ctx: cv.getContext('2d'), tex, W, H: Hh };
  return g;
}

// ---------------------------------------------------------------- 挂钟（原点：表盘中心；set(小时数)）
export function wallClock(r = 0.24) {
  const g = new THREE.Group();
  const rim = cyl(r + 0.025, r + 0.025, 0.05, clay('#2B2F33', 0.5), 48);
  rim.rotation.x = Math.PI / 2;
  g.add(rim);
  const face = cyl(r, r, 0.052, clay('#FFFFFF', 0.6), 48, { cast: false });
  face.rotation.x = Math.PI / 2;
  g.add(face);
  for (let i = 0; i < 12; i++) {
    const tick = box(0.012, i % 3 ? 0.03 : 0.055, 0.005, clay('#2B2F33', 0.6), 0, { cast: false });
    const a = i / 12 * Math.PI * 2;
    tick.position.set(Math.sin(a) * r * 0.82, Math.cos(a) * r * 0.82, 0.03);
    tick.rotation.z = -a;
    g.add(tick);
  }
  const hand = (len, w, c) => {
    const p = new THREE.Group();
    const m = box(w, len, 0.01, clay(c, 0.5), 0, { cast: false });
    m.position.y = len / 2 - 0.02;
    p.add(m);
    p.position.z = 0.035;
    g.add(p);
    return p;
  };
  const hr = hand(r * 0.5, 0.022, '#2B2F33');
  const mn = hand(r * 0.75, 0.014, '#2B2F33');
  g.userData = {
    set(hours) {
      hr.rotation.z = -hours / 12 * Math.PI * 2;
      mn.rotation.z = -(hours % 1) * Math.PI * 2;
    },
  };
  g.userData.set(2.25);
  return g;
}

// ---------------------------------------------------------------- 人物（简洁现代风格；原点脚底，面朝 +z）
export function person() {
  const g = new THREE.Group();
  const skin = clay('#F0C9A6', 0.7), shirt = clay('#3D7EA6', 0.8), pants = clay('#2F3B48', 0.85), hair = clay('#1E1E22', 0.8);
  const torso = mesh(new THREE.CapsuleGeometry(0.17, 0.42, 8, 20), shirt);
  torso.position.y = 1.18;
  g.add(torso);
  const head = new THREE.Group();
  head.add(sphere(0.12, skin));
  const hairCap = mesh(new THREE.SphereGeometry(0.125, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.5), hair);
  hairCap.rotation.x = -0.35;
  head.add(hairCap);
  head.position.y = 1.62;
  g.add(head);
  const limb = (r, l, mat, x, y) => {
    const p = new THREE.Group();
    const m = mesh(new THREE.CapsuleGeometry(r, l, 6, 14), mat);
    m.position.y = -l / 2 - r;
    p.add(m);
    p.position.set(x, y, 0);
    g.add(p);
    return p;
  };
  const armL = limb(0.055, 0.46, shirt, -0.22, 1.42);
  const armR = limb(0.055, 0.46, shirt, 0.22, 1.42);
  const legL = limb(0.075, 0.66, pants, -0.09, 0.84);
  const legR = limb(0.075, 0.66, pants, 0.09, 0.84);
  const handR = new THREE.Group();                      // 右手（遥控器挂点）
  handR.position.set(0, -0.6, 0.02);
  armR.add(handR);
  const handL = new THREE.Group();                      // 左手（钥匙挂点）
  handL.position.set(0, -0.6, 0.02);
  armL.add(handL);
  g.userData = {
    head, armL, armR, handL, handR,
    /** walk：步态相位；amp：步幅；aL/aR：前抬手臂（弧度）；turn：转头 */
    pose({ walk = 0, amp = 0, aL = 0, aR = 0, turn = 0 } = {}) {
      const sw = Math.sin(walk * Math.PI) * amp;
      legL.rotation.x = sw * 0.5;
      legR.rotation.x = -sw * 0.5;
      armL.rotation.x = -sw * 0.4 - aL;
      armR.rotation.x = sw * 0.4 - aR;
      armL.rotation.z = -0.08;
      armR.rotation.z = 0.08;
      head.rotation.y = turn;
    },
  };
  g.userData.pose();
  return g;
}

// ---------------------------------------------------------------- 遥控器（原点：中心，正面朝 +z）
export function remote() {
  const g = new THREE.Group();
  g.add(box(0.055, 0.17, 0.018, plastic('#F7F7F5'), 0.008));
  const scr = box(0.04, 0.035, 0.003, clay('#9FC7D6', 0.3), 0.004, { cast: false });
  scr.position.set(0, 0.045, 0.01);
  g.add(scr);
  const btn = cyl(0.011, 0.011, 0.006, plastic('#E8504A'), 24, { cast: false });
  btn.rotation.x = Math.PI / 2;
  btn.position.set(0, 0.005, 0.011);
  g.add(btn);
  for (let i = 0; i < 6; i++) {
    const b = cyl(0.006, 0.006, 0.005, clay('#C9CDD1', 0.5), 16, { cast: false });
    b.rotation.x = Math.PI / 2;
    b.position.set(-0.012 + (i % 2) * 0.024, -0.03 - Math.floor(i / 2) * 0.02, 0.01);
    g.add(b);
  }
  const ir = sphere(0.006, new THREE.MeshBasicMaterial({ color: '#FF5A4E', toneMapped: false }), { cast: false });
  ir.position.set(0, 0.085, 0.004);
  g.add(ir);
  g.userData = { button: btn, ir };
  return g;
}

export function keys() {
  const g = new THREE.Group();
  g.add(torus(0.02, 0.004, metal('#C9A65A', 0.3)));
  const k = box(0.012, 0.06, 0.003, metal('#B8BDC2', 0.3), 0.002, { cast: false });
  k.position.set(0.01, -0.045, 0);
  k.rotation.z = 0.3;
  g.add(k);
  return g;
}

// ---------------------------------------------------------------- 窗外景（画布：炎热天空、城市楼群、太阳）
function windowViewTex() {
  return canvasTex(1024, 768, (c, w, h) => {
    const sky = c.createLinearGradient(0, 0, 0, h);
    sky.addColorStop(0, '#7FB6E6');
    sky.addColorStop(0.65, '#D9E8F2');
    sky.addColorStop(1, '#F5E7CF');
    c.fillStyle = sky; c.fillRect(0, 0, w, h);
    const sx = w * 0.3, sy = h * 0.24;
    const glowG = c.createRadialGradient(sx, sy, 10, sx, sy, 300);
    glowG.addColorStop(0, 'rgba(255,248,214,1)');
    glowG.addColorStop(0.25, 'rgba(255,214,140,0.7)');
    glowG.addColorStop(1, 'rgba(255,200,120,0)');
    c.fillStyle = glowG; c.fillRect(0, 0, w, h);
    c.fillStyle = '#FFFBEA';
    c.beginPath(); c.arc(sx, sy, 62, 0, Math.PI * 2); c.fill();
    const r = rng(11);
    for (let L = 0; L < 2; L++) {
      let x = -20;
      while (x < w) {
        const bw = 70 + r() * 120, bh = (L ? 180 : 300) + r() * (L ? 160 : 220);
        c.fillStyle = L ? '#9FB3C4' : '#C3D1DC';
        c.fillRect(x, h - bh, bw, bh);
        c.fillStyle = L ? 'rgba(255,255,255,0.35)' : 'rgba(255,255,255,0.45)';
        for (let yy = h - bh + 18; yy < h - 20; yy += 34) for (let xx = x + 12; xx < x + bw - 16; xx += 26) c.fillRect(xx, yy, 12, 16);
        x += bw + 10 + r() * 30;
      }
    }
  });
}

// ---------------------------------------------------------------- 整间屋子
export function buildRoom() {
  const { w, d, h, wall: T } = ROOM;
  const g = new THREE.Group();
  const wallMat = warmable(MOD.wall, 0.92);
  const cutMat = clay(MOD.cut, 0.9);
  const floorMat = clay(MOD.floor, 0.7);
  // 墙体：内表面 wallMat，切口（顶面与前端面）用 cutMat，让剖面厚度清楚可见
  const wallBox = (x0, x1, y0, y1, z0, z1) => {
    const geo = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0);
    const mats = [wallMat, wallMat, cutMat, wallMat, cutMat, wallMat];   // +x -x +y -y +z -z
    const m = new THREE.Mesh(geo, mats);
    m.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
    m.castShadow = true; m.receiveShadow = true;
    g.add(m);
    return m;
  };
  const X0 = -w / 2, X1 = w / 2, Zb = -d / 2, Zf = d / 2;
  // 地板（带厚度）与踢脚线
  const slab = box(w + 2 * T, 0.18, d + T, floorMat, 0);
  slab.position.set(0, -0.09, -T / 2);
  g.add(slab);
  const slabEdge = box(w + 2 * T + 0.01, 0.1, d + T + 0.01, clay('#9C8670', 0.8), 0, { cast: false });
  slabEdge.position.set(0, -0.23, -T / 2);
  g.add(slabEdge);
  // 后墙（窗洞 x∈[-2.3,-0.5], y∈[0.85,2.45]）
  const WX0 = -2.3, WX1 = -0.5, WY0 = 0.85, WY1 = 2.45;
  wallBox(X0 - T, WX0, 0, h, Zb - T, Zb);
  wallBox(WX1, X1 + T, 0, h, Zb - T, Zb);
  wallBox(WX0, WX1, 0, WY0, Zb - T, Zb);
  wallBox(WX0, WX1, WY1, h, Zb - T, Zb);
  // 左墙
  wallBox(X0 - T, X0, 0, h, Zb, Zf);
  // 右墙（门洞 z∈[0.55,1.55], y<2.1）
  const DZ0 = 0.55, DZ1 = 1.55, DH = 2.1;
  wallBox(X1, X1 + T, 0, h, Zb, DZ0);
  wallBox(X1, X1 + T, 0, h, DZ1, Zf);
  wallBox(X1, X1 + T, DH, h, DZ0, DZ1);
  // 窗：铝合金框 + 玻璃 + 窗外景
  const frameMat = clay('#5E6873', 0.45);
  const fz = Zb - T / 2;
  for (const [x, y, ww, hh] of [[(WX0 + WX1) / 2, WY0, WX1 - WX0, 0.05], [(WX0 + WX1) / 2, WY1, WX1 - WX0, 0.05],
    [WX0, (WY0 + WY1) / 2, 0.05, WY1 - WY0], [WX1, (WY0 + WY1) / 2, 0.05, WY1 - WY0], [(WX0 + WX1) / 2, (WY0 + WY1) / 2, 0.035, WY1 - WY0]]) {
    const f = box(ww, hh, 0.07, frameMat, 0, { cast: false });
    f.position.set(x, y, fz);
    g.add(f);
  }
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(WX1 - WX0, WY1 - WY0),
    new THREE.MeshPhysicalMaterial({ color: '#DFF1FF', roughness: 0.05, transparent: true, opacity: 0.18, depthWrite: false }));
  glass.position.set((WX0 + WX1) / 2, (WY0 + WY1) / 2, fz);
  g.add(glass);
  const sill = box(WX1 - WX0 + 0.16, 0.04, 0.2, clay('#ECE8E1', 0.6), 0.01);
  sill.position.set((WX0 + WX1) / 2, WY0 - 0.02, Zb + 0.06);
  g.add(sill);
  const view = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.95),
    new THREE.MeshBasicMaterial({ map: windowViewTex(), toneMapped: false }));
  view.position.set((WX0 + WX1) / 2, (WY0 + WY1) / 2 + 0.1, Zb - 0.9);
  g.add(view);
  // 阳光：从窗口斜照到地板的半透明光带
  const beamGeo = new THREE.BufferGeometry();
  const bv = [WX0, WY1, Zb, WX1, WY1, Zb, WX1, WY0, Zb, WX0, WY0, Zb,
    WX0 + 0.7, 0.01, Zb + 1.6, WX1 + 0.7, 0.01, Zb + 1.6, WX1 + 0.7, 0.01, Zb + 0.6, WX0 + 0.7, 0.01, Zb + 0.6];
  beamGeo.setAttribute('position', new THREE.Float32BufferAttribute(bv, 3));
  beamGeo.setIndex([0, 1, 5, 0, 5, 4, 3, 2, 6, 3, 6, 7, 0, 4, 7, 0, 7, 3, 1, 2, 6, 1, 6, 5]);
  const beamMat = new THREE.MeshBasicMaterial({ color: '#FFE3A3', transparent: true, opacity: 0.16, depthWrite: false,
    side: THREE.DoubleSide, blending: THREE.AdditiveBlending });
  const beam = new THREE.Mesh(beamGeo, beamMat);
  g.add(beam);
  const patch = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 1.0),
    new THREE.MeshBasicMaterial({ color: '#FFE7B0', transparent: true, opacity: 0.32, depthWrite: false }));
  patch.rotation.x = -Math.PI / 2;
  patch.position.set((WX0 + WX1) / 2 + 0.7, 0.012, Zb + 1.1);
  g.add(patch);
  // 门
  const doorPivot = new THREE.Group();
  doorPivot.position.set(X1 + T / 2, 0, DZ1);
  const door = box(0.05, DH - 0.02, DZ1 - DZ0 - 0.02, clay('#B48A62', 0.6), 0.01);
  door.position.set(0, DH / 2, -(DZ1 - DZ0) / 2);
  const knob = sphere(0.03, metal('#C8CCD0', 0.3), { cast: false });
  knob.position.set(-0.05, DH / 2 - 0.05, -(DZ1 - DZ0) + 0.12);
  door.add(knob);
  doorPivot.add(door);
  g.add(doorPivot);
  // 阳台（左墙外的空调平台）
  const balc = box(1.3, 0.14, 1.8, clay('#D9D6D0', 0.8), 0);
  balc.position.set(X0 - T - 0.65, -0.07, 1.25);
  g.add(balc);
  const railMat = new THREE.MeshPhysicalMaterial({ color: '#CFE6F2', roughness: 0.1, transparent: true, opacity: 0.25, depthWrite: false });
  for (const [x, z, ww, dd] of [[X0 - T - 1.28, 1.25, 0.03, 1.8], [X0 - T - 0.65, 2.13, 1.3, 0.03]]) {
    const r = box(ww, 0.9, dd, railMat, 0, { cast: false });
    r.position.set(x, 0.45, z);
    g.add(r);
    const top = box(ww + 0.02, 0.04, dd + 0.02, metal('#8D959C', 0.4), 0, { cast: false });
    top.position.set(x, 0.92, z);
    g.add(top);
  }
  const outdoor = acOutdoor();
  outdoor.position.set(X0 - T - 0.62, 0, 1.15);
  g.add(outdoor);
  // 室内机、管路
  const indoor = acIndoor();
  indoor.position.set(1.45, 2.6, Zb + 0.14);
  g.add(indoor);
  const pipePts = [[0.78, 2.66, Zb + 0.06], [-2.6, 2.66, Zb + 0.06], [X0 + 0.05, 2.66, Zb + 0.06], [X0 + 0.05, 2.66, Zb + 0.3],
    [X0 - T - 0.08, 2.66, Zb + 0.3], [X0 - T - 0.08, 2.66, 0.9], [X0 - T - 0.08, 0.95, 0.9], [X0 - T - 0.2, 0.42, 0.98]]
    .map(p => new THREE.Vector3(...p));
  const pipeCurve = new THREE.CatmullRomCurve3(pipePts, false, 'catmullrom', 0.05);
  const pipe = mesh(new THREE.TubeGeometry(pipeCurve, 160, 0.035, 10, false), clay('#F2F1EE', 0.6));
  g.add(pipe);
  // 电视与电视柜
  const set = tv();
  set.position.set(1.4, 1.38, Zb + 0.04);
  g.add(set);
  const cab = box(2.3, 0.42, 0.42, clay('#F3F0EA', 0.55), 0.02);
  cab.position.set(1.4, 0.21, Zb + 0.22);
  g.add(cab);
  const cabTop = box(2.32, 0.03, 0.44, clay('#B8936C', 0.6), 0.01, { cast: false });
  cabTop.position.set(1.4, 0.435, Zb + 0.22);
  g.add(cabTop);
  // 挂钟
  const clock = wallClock();
  clock.position.set(0.05, 2.15, Zb + 0.03);
  g.add(clock);
  // 沙发（靠左墙，面朝 +x）
  const sofaMat = warmable('#8A9BAE', 0.95);
  const sofa = new THREE.Group();
  const seat = box(0.85, 0.42, 2.1, sofaMat, 0.08); seat.position.set(0, 0.21, 0); sofa.add(seat);
  const back = box(0.22, 0.5, 2.1, sofaMat, 0.08); back.position.set(-0.32, 0.62, 0); sofa.add(back);
  for (const z of [-1.0, 1.0]) { const arm = box(0.85, 0.58, 0.18, sofaMat, 0.07); arm.position.set(0, 0.29, z); sofa.add(arm); }
  for (const z of [-0.45, 0.45]) {
    const c = box(0.6, 0.12, 0.86, warmable('#9CAEC0', 0.95), 0.05); c.position.set(0.06, 0.47, z); sofa.add(c);
  }
  const pillow = box(0.12, 0.34, 0.34, clay('#E7C27C', 0.9), 0.06); pillow.position.set(-0.16, 0.66, 0.6); pillow.rotation.y = 0.2;
  sofa.add(pillow);
  sofa.position.set(X0 + 0.48, 0, 0.35);
  g.add(sofa);
  // 地毯、茶几、绿植
  const rug = mesh(new THREE.PlaneGeometry(2.4, 2.0), clay('#E9E2D6', 0.95), { cast: false });
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(-0.9, 0.006, 0.4);
  g.add(rug);
  const tableTop = cyl(0.42, 0.42, 0.04, clay('#FFFFFF', 0.4), 48);
  tableTop.position.set(-0.85, 0.42, 0.45);
  g.add(tableTop);
  const tableLeg = cyl(0.04, 0.12, 0.4, metal('#3A3F44', 0.5), 20);
  tableLeg.position.set(-0.85, 0.2, 0.45);
  g.add(tableLeg);
  const cup = cyl(0.04, 0.035, 0.09, clay('#E07A5F', 0.5), 20);
  cup.position.set(-0.75, 0.485, 0.35);
  g.add(cup);
  const plant = new THREE.Group();
  const pot = cyl(0.2, 0.15, 0.4, clay('#E9E6E0', 0.7), 32); pot.position.y = 0.2; plant.add(pot);
  const R = rng(5);
  for (let i = 0; i < 9; i++) {
    const leaf = mesh(new THREE.SphereGeometry(0.17, 16, 10), clay(i % 2 ? '#4E8C5A' : '#62A06C', 0.8));
    leaf.scale.set(0.6, 1.2, 0.35);
    const a = i / 9 * Math.PI * 2;
    leaf.position.set(Math.cos(a) * 0.14, 0.62 + R() * 0.35, Math.sin(a) * 0.14);
    leaf.rotation.set(Math.sin(a) * 0.5, a, Math.cos(a) * 0.5);
    plant.add(leaf);
  }
  plant.position.set(X0 + 0.35, 0, Zb + 0.4);
  g.add(plant);
  // 冷气带（室内机出风口下方）
  const cold = coldRibbons();
  cold.position.set(1.45, 2.42, Zb + 0.3);
  g.add(cold);

  return {
    group: g, indoor, outdoor, pipeCurve, tv: set, clock, doorPivot, cold, beam, beamMat, patch, wallMat, sofaMat,
    sofa, window: { x0: WX0, x1: WX1, y0: WY0, y1: WY1, z: Zb },
  };
}

// ---------------------------------------------------------------- 冷气（半透明蓝色气带，从出风口向前下方卷出）
function coldRibbons() {
  const g = new THREE.Group();
  const R = rng(9);
  const ribbons = [];
  for (let i = 0; i < 7; i++) {
    const x = (i / 6 - 0.5) * 1.1;
    const pts = [];
    for (let k = 0; k <= 14; k++) {
      const u = k / 14;
      pts.push(new THREE.Vector3(x * (1 + u * 0.5) + Math.sin(u * 3 + i) * 0.06, -u * 1.5 - u * u * 0.3, u * 1.6 + Math.sin(u * 4 + R() * 6) * 0.05));
    }
    const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 56, 0.022, 6, false);
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: '#9DD3FF', transparent: true, opacity: 0.5, depthWrite: false }));
    g.add(m);
    ribbons.push({ m, count: geo.index.count, phase: R() });
  }
  g.userData = {
    set(k, t) {
      g.visible = k > 0.01;
      ribbons.forEach(r => {
        const u = (t * 0.5 + r.phase) % 1;
        const head = Math.floor(r.count * clamp01(0.35 + u * 0.65) / 6) * 6;
        r.m.geometry.setDrawRange(0, Math.floor(head * clamp01(k) / 6) * 6);
        r.m.material.opacity = 0.42 * clamp01(k) * (1 - 0.55 * u);
      });
    },
  };
  return g;
}

/** 热粒子（InstancedMesh）：update(t, density, path) 中 path(u, seeds) → [x,y,z]，u∈[0,1]。 */
export function heatDots(n, { color = MOD.heat, r = 0.045, seed = 1 } = {}) {
  const inst = new THREE.InstancedMesh(new THREE.SphereGeometry(r, 12, 8),
    new THREE.MeshBasicMaterial({ color, toneMapped: false, transparent: true, opacity: 0.92 }), n);
  inst.castShadow = false;
  inst.frustumCulled = false;
  const Rr = rng(seed);
  const seeds = Array.from({ length: n }, () => [Rr(), Rr(), Rr(), Rr()]);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(), pos = new THREE.Vector3();
  inst.userData = {
    update(t, density, path, speed = 0.3, fade = 0.12) {
      for (let i = 0; i < n; i++) {
        const s = seeds[i];
        const u = (t * speed * (0.75 + 0.5 * s[1]) + s[2]) % 1;
        const p = path(u, s);
        pos.set(p[0], p[1], p[2]);
        const life = Math.min(1, u / fade, (1 - u) / fade);
        const k = s[0] < density ? life * (0.7 + 0.5 * s[3]) : 0.0001;
        sc.setScalar(Math.max(0.0001, k));
        m4.compose(pos, q, sc);
        inst.setMatrixAt(i, m4);
      }
      inst.instanceMatrix.needsUpdate = true;
    },
  };
  return inst;
}
