// 道具库：国风房间、空调内外机、遥控器、温度计、算盘、杆秤、印章、卷轴、灯笼、窗棂、电表、热流粒子等。
// 每个工厂函数返回 THREE.Group（局部原点在物体底部中心或几何中心，注释里说明），动画参数挂在 userData 上。
import {
  THREE, PAL, box, cyl, sphere, torus, mesh, group, at, clay, lacquer, metal, glow, outline, textPlane, canvasTex,
  rng, clamp01, lerp, RoundedBoxGeometry,
} from './engine.js';

// ---------------------------------------------------------------- 空调室内机（原点：机身中心）
export function acIndoor({ w = 3.2, h = 0.95, d = 0.75 } = {}) {
  const g = new THREE.Group();
  const body = box(w, h, d, clay('#F4F0E8', 0.45), 0.18, { ink: 0.012 });
  g.add(body);
  const front = box(w * 0.96, h * 0.55, 0.06, clay('#FBF8F2', 0.35), 0.03);
  at(front, 0, h * 0.1, d / 2 + 0.01);
  g.add(front);
  // 出风口导风板（可开合）
  const louver = box(w * 0.88, 0.07, 0.22, clay('#E3DDD2', 0.5), 0.03);
  const pivot = new THREE.Group();
  pivot.position.set(0, -h * 0.36, d / 2 - 0.05);
  louver.position.set(0, 0, 0.1);
  pivot.add(louver);
  g.add(pivot);
  const slot = box(w * 0.9, 0.12, 0.05, clay('#3A3530', 0.9), 0.02, { cast: false });
  at(slot, 0, -h * 0.36, d / 2 - 0.06);
  g.add(slot);
  // 温度显示屏（画布纹理，可改数字）
  const cv = document.createElement('canvas');
  cv.width = 256; cv.height = 128;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.31), new THREE.MeshBasicMaterial({ map: tex, transparent: true }));
  screen.position.set(w * 0.3, h * 0.08, d / 2 + 0.05);
  g.add(screen);
  const led = sphere(0.035, glow(PAL.jade, 1.4), { cast: false });
  led.position.set(w * 0.42, -h * 0.12, d / 2 + 0.05);
  g.add(led);
  let lastText = null;
  g.userData = {
    louver: pivot, led,
    /** 设置导风板开度 0–1、显示文字与指示灯状态 */
    set(open, text, on = true) {
      pivot.rotation.x = lerp(0, 0.9, clamp01(open));
      led.material.emissiveIntensity = on ? 1.4 : 0.0;
      led.material.color.set(on ? PAL.jade : '#7A746A');
      if (text !== lastText) {
        lastText = text;
        const c = cv.getContext('2d');
        c.clearRect(0, 0, 256, 128);
        if (text) {
          c.fillStyle = on ? '#2E8F7A' : '#9A9288';
          c.font = '700 84px "NotoSansSC"';
          c.textAlign = 'center'; c.textBaseline = 'middle';
          c.fillText(text, 128, 66);
        }
        tex.needsUpdate = true;
      }
    },
  };
  g.userData.set(0, '26°', true);
  return g;
}

// ---------------------------------------------------------------- 空调室外机（原点：底部中心）
export function acOutdoor({ s = 1 } = {}) {
  const g = new THREE.Group();
  const body = box(2.2 * s, 1.6 * s, 0.9 * s, clay('#E9E4DA', 0.55), 0.08 * s, { ink: 0.01 });
  body.position.y = 0.8 * s;
  g.add(body);
  const grill = torus(0.55 * s, 0.04 * s, clay('#5A544C', 0.8));
  grill.position.set(-0.3 * s, 0.82 * s, 0.46 * s);
  g.add(grill);
  const hub = cyl(0.1 * s, 0.1 * s, 0.06 * s, clay('#5A544C', 0.8));
  hub.rotation.x = Math.PI / 2;
  hub.position.set(-0.3 * s, 0.82 * s, 0.44 * s);
  g.add(hub);
  const fan = new THREE.Group();
  for (let i = 0; i < 3; i++) {
    const blade = box(0.18 * s, 0.48 * s, 0.03 * s, clay('#7D766C', 0.7), 0.04 * s);
    blade.position.y = 0.26 * s;
    const arm = new THREE.Group();
    arm.rotation.z = i * Math.PI * 2 / 3;
    arm.add(blade);
    fan.add(arm);
  }
  fan.position.set(-0.3 * s, 0.82 * s, 0.4 * s);
  g.add(fan);
  for (let i = 0; i < 6; i++) {
    const fin = box(0.55 * s, 0.03 * s, 0.05 * s, clay('#CFC8BC', 0.7), 0, { cast: false });
    fin.position.set(0.68 * s, (0.35 + i * 0.18) * s, 0.46 * s);
    g.add(fin);
  }
  g.userData = { fan };
  return g;
}

// ---------------------------------------------------------------- 遥控器（原点：中心，正面朝 +z）
export function remote() {
  const g = new THREE.Group();
  g.add(box(0.55, 1.5, 0.16, clay('#F6F2EA', 0.45), 0.08, { ink: 0.02 }));
  const scr = box(0.4, 0.34, 0.03, clay('#BFD8CF', 0.4), 0.03, { cast: false });
  scr.position.set(0, 0.42, 0.085);
  g.add(scr);
  const btn = cyl(0.11, 0.11, 0.05, lacquer(PAL.cinnabar), 32);
  btn.rotation.x = Math.PI / 2;
  btn.position.set(0, -0.05, 0.09);
  g.add(btn);
  for (let i = 0; i < 6; i++) {
    const b = cyl(0.055, 0.055, 0.04, clay('#D9D2C6', 0.6), 20, { cast: false });
    b.rotation.x = Math.PI / 2;
    b.position.set(-0.13 + (i % 2) * 0.26, -0.33 - Math.floor(i / 2) * 0.17, 0.085);
    g.add(b);
  }
  g.userData = { button: btn };
  return g;
}

// ---------------------------------------------------------------- 温度计（原点：底部，读数 0–1 映射玻璃柱高度）
export function thermometer({ h = 3, color = PAL.cinnabar } = {}) {
  const g = new THREE.Group();
  const tube = cyl(0.16, 0.16, h, new THREE.MeshPhysicalMaterial({ color: '#FFFFFF', roughness: 0.1, transmission: 0.6,
    transparent: true, opacity: 0.45 }), 32, { cast: false });
  tube.position.y = h / 2 + 0.25;
  g.add(tube);
  const bulb = sphere(0.3, glow(color, 0.35));
  bulb.position.y = 0.25;
  g.add(bulb);
  const fluid = cyl(0.09, 0.09, 1, glow(color, 0.35), 24, { cast: false });
  g.add(fluid);
  const board = box(0.7, h + 0.8, 0.12, clay(PAL.wood2, 0.7), 0.06, { ink: 0.01 });
  board.position.set(0, h / 2 + 0.2, -0.22);
  g.add(board);
  for (let i = 0; i <= 10; i++) {
    const tick = box(i % 5 === 0 ? 0.24 : 0.14, 0.025, 0.02, clay(PAL.paper, 0.8), 0, { cast: false });
    tick.position.set(0.2, 0.55 + (h - 0.4) * i / 10, -0.15);
    g.add(tick);
  }
  g.userData = {
    set(v) {
      const len = Math.max(0.05, (h - 0.3) * clamp01(v));
      fluid.scale.y = len;
      fluid.position.y = 0.4 + len / 2;
    },
  };
  g.userData.set(0.5);
  return g;
}

// ---------------------------------------------------------------- 国风房间（原点：地面中心；后墙在 z=-depth/2）
export function chineseRoom({ w = 12, h = 7.5, depth = 9, wall = '#E8DCC4', floor = '#B98A5E', moonWindow = true } = {}) {
  const g = new THREE.Group();
  const fl = mesh(new THREE.PlaneGeometry(w, depth), clay(floor, 0.85), { cast: false });
  fl.rotation.x = -Math.PI / 2;
  g.add(fl);
  for (let i = 1; i < 10; i++) {                       // 木地板缝
    const ln = box(w, 0.005, 0.02, clay('#8E6640', 0.9), 0, { cast: false });
    ln.position.set(0, 0.003, -depth / 2 + depth * i / 10);
    g.add(ln);
  }
  const back = mesh(new THREE.PlaneGeometry(w, h), clay(wall, 0.92), { cast: false });
  back.position.set(0, h / 2, -depth / 2);
  g.add(back);
  const side = mesh(new THREE.PlaneGeometry(depth, h), clay('#E1D3B8', 0.92), { cast: false });
  side.position.set(-w / 2, h / 2, 0);
  side.rotation.y = Math.PI / 2;
  g.add(side);
  // 檀木踢脚与梁
  const skirt = box(w, 0.25, 0.08, clay(PAL.wood, 0.7), 0, { cast: false });
  skirt.position.set(0, 0.125, -depth / 2 + 0.04);
  g.add(skirt);
  const beam = box(w, 0.45, 0.4, clay(PAL.wood, 0.7));
  beam.position.set(0, h - 0.22, -depth / 2 + 0.2);
  g.add(beam);
  let win = null;
  if (moonWindow) {
    win = moonWindowProp(1.9);
    win.position.set(-2.6, 3.5, -depth / 2 + 0.06);
    g.add(win);
  }
  g.userData = { win, back, w, h, depth };
  return g;
}

/** 月洞窗：圆形窗框 + 冰裂纹窗棂，窗外是水墨远山（原点：窗心）。 */
export function moonWindowProp(r = 1.8, outsideTex = null) {
  const g = new THREE.Group();
  const frame = torus(r, 0.16, clay(PAL.wood, 0.65));
  g.add(frame);
  const sky = new THREE.Mesh(new THREE.CircleGeometry(r, 64), new THREE.MeshBasicMaterial({
    map: outsideTex || canvasTex(512, 512, (c) => {
      const grd = c.createLinearGradient(0, 0, 0, 512);
      grd.addColorStop(0, '#F6E7C8'); grd.addColorStop(1, '#F2D7A8');
      c.fillStyle = grd; c.fillRect(0, 0, 512, 512);
      const r_ = rng(11);
      for (let L = 0; L < 3; L++) {
        c.beginPath(); c.moveTo(0, 512);
        for (let x = 0; x <= 512; x += 8) c.lineTo(x, 300 + L * 50 - 70 * Math.pow(Math.abs(Math.sin(x * 0.012 + L * 1.7 + r_())), 1.5));
        c.lineTo(512, 512); c.closePath();
        c.fillStyle = `rgba(60,80,82,${0.25 + L * 0.22})`; c.fill();
      }
    }),
  }));
  sky.position.z = -0.02;
  g.add(sky);
  // 冰裂纹窗棂：随机多边形网格的细木条
  const r_ = rng(21);
  const pts = [];
  for (let i = 0; i < 14; i++) pts.push([(r_() - 0.5) * 2 * r, (r_() - 0.5) * 2 * r]);
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i], b = pts[(i * 5 + 3) % pts.length];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (len > r * 1.3) continue;
    const bar = box(len, 0.05, 0.05, clay(PAL.wood2, 0.7), 0, { cast: false });
    bar.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.02);
    bar.rotation.z = Math.atan2(b[1] - a[1], b[0] - a[0]);
    if (Math.hypot(bar.position.x, bar.position.y) < r * 0.82) g.add(bar);
  }
  return g;
}

// ---------------------------------------------------------------- 红灯笼（原点：顶部挂点）
export function lantern(s = 1) {
  const g = new THREE.Group();
  const body = mesh(new THREE.SphereGeometry(0.6 * s, 32, 20), lacquer(PAL.cinnabar, 0.45));
  body.scale.y = 0.82;
  body.position.y = -0.9 * s;
  g.add(body);
  for (let i = 0; i < 8; i++) {
    const rib = torus(0.6 * s, 0.012 * s, clay(PAL.rouge, 0.6), Math.PI);
    rib.rotation.y = i * Math.PI / 8;
    rib.rotation.z = Math.PI / 2;
    rib.scale.y = 0.82;
    rib.position.y = -0.9 * s;
    g.add(rib);
  }
  const top = cyl(0.25 * s, 0.25 * s, 0.14 * s, clay(PAL.gold, 0.5));
  top.position.y = -0.38 * s;
  g.add(top);
  const bot = top.clone();
  bot.position.y = -1.42 * s;
  g.add(bot);
  const cord = cyl(0.015 * s, 0.015 * s, 0.4 * s, clay(PAL.ink, 0.8));
  cord.position.y = -0.15 * s;
  g.add(cord);
  for (let i = 0; i < 9; i++) {
    const tassel = cyl(0.012 * s, 0.012 * s, 0.5 * s, clay(PAL.rouge, 0.8), 6, { cast: false });
    tassel.position.set((i - 4) * 0.025 * s, -1.75 * s, 0);
    g.add(tassel);
  }
  return g;
}

// ---------------------------------------------------------------- 算盘（原点：中心；userData.set(行, 值) 拨珠）
export function abacus({ cols = 7, w = 5, h = 2.6 } = {}) {
  const g = new THREE.Group();
  const wood = clay(PAL.wood, 0.6);
  const fr = [box(w, 0.2, 0.3, wood, 0.05), box(w, 0.2, 0.3, wood, 0.05), box(0.2, h, 0.3, wood, 0.05), box(0.2, h, 0.3, wood, 0.05)];
  fr[0].position.y = h / 2; fr[1].position.y = -h / 2; fr[2].position.x = -w / 2; fr[3].position.x = w / 2;
  fr.forEach(f => g.add(f));
  const beam = box(w, 0.12, 0.26, wood, 0.03);
  beam.position.y = h * 0.22;
  g.add(beam);
  const beads = [];
  const beadGeo = new THREE.SphereGeometry(0.2, 24, 12);
  const beadMat = lacquer('#3A2A22', 0.35);
  for (let c = 0; c < cols; c++) {
    const x = -w / 2 + (c + 0.5) * w / cols;
    const rod = cyl(0.025, 0.025, h, metal('#C9A15E', 0.4), 8, { cast: false });
    rod.position.x = x;
    g.add(rod);
    const col = [];
    for (let k = 0; k < 6; k++) {
      const b = mesh(beadGeo, beadMat);
      b.scale.set(1.25, 0.62, 1.25);
      b.position.x = x;
      g.add(b);
      col.push(b);
    }
    beads.push(col);
  }
  const top = h / 2 - 0.1, mid = h * 0.22, bot = -h / 2 + 0.1;
  g.userData = {
    beads,
    /** 第 c 列显示 0–9（上珠 1 颗当 5，下珠 5 颗当 1），k 为拨珠动画进度 */
    set(c, v, k = 1) {
      const col = beads[c];
      const up = v >= 5 ? 1 : 0, low = v % 5;
      col[0].position.y = lerp(top - 0.16, mid + 0.22, up * k);
      for (let i = 0; i < 5; i++) {
        const raised = i < low ? k : 0;
        const rest = bot + 0.16 + (4 - i) * 0.26;
        const active = mid - 0.22 - i * 0.26;
        col[i + 1].position.y = lerp(rest, active, raised);
      }
    },
  };
  for (let c = 0; c < cols; c++) g.userData.set(c, 0, 1);
  return g;
}

// ---------------------------------------------------------------- 杆秤（原点：提纽；userData.set(倾角)）
export function steelyard({ len = 6 } = {}) {
  const g = new THREE.Group();
  const arm = new THREE.Group();
  const rod = cyl(0.06, 0.09, len, clay(PAL.wood2, 0.6), 24);
  rod.rotation.z = Math.PI / 2;
  rod.position.x = len * 0.15;
  arm.add(rod);
  for (let i = 0; i < 16; i++) {
    const star = sphere(0.025, metal('#E2C27A', 0.3), { cast: false });
    star.position.set(-len * 0.1 + i * len * 0.045, 0.07, 0.04);
    arm.add(star);
  }
  const hook = torus(0.12, 0.02, metal('#8B8378', 0.4), Math.PI * 1.4);
  hook.position.set(-len * 0.33, -0.25, 0);
  arm.add(hook);
  const pan = new THREE.Group();
  const dish = mesh(new THREE.CylinderGeometry(0.75, 0.55, 0.12, 40), clay('#8C6A48', 0.6));
  dish.position.y = -1.3;
  pan.add(dish);
  for (let i = 0; i < 3; i++) {
    const cord = cyl(0.01, 0.01, 1.3, clay(PAL.ink, 0.8), 6, { cast: false });
    const a = i * Math.PI * 2 / 3;
    cord.position.set(Math.cos(a) * 0.35, -0.65, Math.sin(a) * 0.35);
    cord.rotation.z = Math.cos(a) * 0.25;
    cord.rotation.x = -Math.sin(a) * 0.25;
    pan.add(cord);
  }
  pan.position.set(-len * 0.33, -0.25, 0);
  arm.add(pan);
  const weight = new THREE.Group();
  const wt = mesh(new THREE.CylinderGeometry(0.22, 0.32, 0.5, 6), metal('#5D564C', 0.45));
  wt.position.y = -0.85;
  weight.add(wt);
  const wc = cyl(0.01, 0.01, 0.6, clay(PAL.ink, 0.8), 6, { cast: false });
  wc.position.y = -0.3;
  weight.add(wc);
  weight.position.set(len * 0.45, 0, 0);
  arm.add(weight);
  g.add(arm);
  const knob = torus(0.1, 0.025, metal('#8B8378', 0.4));
  knob.position.y = 0.2;
  g.add(knob);
  g.userData = {
    arm, pan, weight,
    set(tilt, wx = null) {
      arm.rotation.z = tilt;
      pan.rotation.z = -tilt;
      weight.rotation.z = -tilt;
      if (wx !== null) weight.position.x = wx;
    },
  };
  return g;
}

// ---------------------------------------------------------------- 印章（原点：印面中心；文字为阴刻白字）
export function seal(text = '省', { s = 1, color = PAL.cinnabar } = {}) {
  const g = new THREE.Group();
  const body = box(1.2 * s, 1.5 * s, 1.2 * s, clay('#D9C9A8', 0.55), 0.08 * s, { ink: 0.01 });
  body.position.y = 0.75 * s;
  g.add(body);
  const knob = mesh(new THREE.SphereGeometry(0.45 * s, 32, 16), clay('#CDB88F', 0.5));
  knob.scale.y = 0.7;
  knob.position.y = 1.62 * s;
  g.add(knob);
  const face = textPlane(text, { w: 1.1 * s, h: 1.1 * s, px: 256, size: 190, color: '#F6EEE0', bg: color });
  face.rotation.x = Math.PI / 2;
  face.position.y = -0.005;
  g.add(face);
  return g;
}

// ---------------------------------------------------------------- 卷轴（原点：中心；userData.set(展开 0–1)）
export function scroll(text, { w = 6, h = 2, font = 'MaShanZheng', size = 300, color = PAL.ink } = {}) {
  const g = new THREE.Group();
  const paperTex = canvasTex(1536, 512, (c) => {
    c.fillStyle = '#F4EAD3'; c.fillRect(0, 0, 1536, 512);
    c.strokeStyle = '#B88A4A'; c.lineWidth = 10; c.strokeRect(36, 36, 1464, 440);
    c.fillStyle = color; c.font = `${size}px "${font}"`; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(text, 768, 270);
  });
  const sheet = mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ map: paperTex, roughness: 0.9 }), { cast: true });
  g.add(sheet);
  const rodL = cyl(0.12, 0.12, h + 0.5, lacquer(PAL.rouge, 0.4), 24);
  const rodR = rodL.clone();
  g.add(rodL, rodR);
  for (const r of [rodL, rodR]) {
    for (const yy of [-1, 1]) {
      const cap = cyl(0.16, 0.16, 0.16, clay(PAL.gold, 0.4), 24);
      cap.position.y = yy * (h + 0.5) / 2;
      r.add(cap);
    }
  }
  g.userData = {
    set(k) {
      const ww = Math.max(0.001, w * clamp01(k));
      sheet.scale.x = ww / w;
      paperTex.offset.x = 0;
      rodL.position.x = -ww / 2 - 0.1;
      rodR.position.x = ww / 2 + 0.1;
      sheet.visible = k > 0.01;
    },
  };
  g.userData.set(1);
  return g;
}

// ---------------------------------------------------------------- 电表（原点：中心；userData.set(转盘角度, 读数文字)）
export function meter() {
  const g = new THREE.Group();
  g.add(box(1.8, 2.4, 0.6, clay('#E6E0D3', 0.55), 0.12, { ink: 0.012 }));
  const glass = box(1.5, 1.4, 0.08, new THREE.MeshPhysicalMaterial({ color: '#DDEFF2', roughness: 0.05, transmission: 0.5,
    transparent: true, opacity: 0.4 }), 0.1, { cast: false });
  glass.position.set(0, 0.35, 0.32);
  g.add(glass);
  const disc = cyl(0.5, 0.5, 0.04, metal('#C9C2B4', 0.3), 48, { cast: false });
  disc.position.set(0, 0.05, 0.22);
  const mark = box(0.12, 0.05, 0.06, lacquer(PAL.cinnabar), 0, { cast: false });
  mark.position.set(0.42, 0.03, 0);
  disc.add(mark);
  g.add(disc);
  const cv = document.createElement('canvas');
  cv.width = 512; cv.height = 128;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  const read = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.3), new THREE.MeshBasicMaterial({ map: tex }));
  read.position.set(0, 0.72, 0.3);
  g.add(read);
  let last = null;
  g.userData = {
    set(angle, text) {
      disc.rotation.y = angle;
      if (text !== last) {
        last = text;
        const c = cv.getContext('2d');
        c.fillStyle = '#2B2622'; c.fillRect(0, 0, 512, 128);
        c.fillStyle = '#F2E4C4'; c.font = '700 92px "NotoSansSC"'; c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText(text, 256, 68);
        tex.needsUpdate = true;
      }
    },
  };
  g.userData.set(0, '0000.0');
  return g;
}

// ---------------------------------------------------------------- 热流粒子（InstancedMesh；update(t, rate, path) 按速率生成）
export function particles(n = 160, { color = PAL.heat, r = 0.09, seed = 1 } = {}) {
  const geo = new THREE.SphereGeometry(r, 12, 8);
  const mat = glow(color, 0.6);
  const inst = new THREE.InstancedMesh(geo, mat, n);
  inst.castShadow = false;
  const R = rng(seed);
  const seeds = Array.from({ length: n }, () => [R(), R(), R(), R()]);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(), pos = new THREE.Vector3();
  inst.userData = {
    /** path(u, s) → [x,y,z]：u∈[0,1] 沿路径进度，s 为每粒随机种子；density∈[0,1] 控制可见粒子比例 */
    update(t, density, path, speed = 0.35) {
      for (let i = 0; i < n; i++) {
        const [a, b, c, d] = seeds[i];
        const vis = a < density;
        const u = (t * speed * (0.7 + 0.6 * b) + c) % 1;
        const p = path(u, [a, b, c, d]);
        pos.set(p[0], p[1], p[2]);
        const s = vis ? Math.sin(Math.PI * u) * (0.6 + 0.6 * d) : 0.0001;
        sc.set(s, s, s);
        m4.compose(pos, q, sc);
        inst.setMatrixAt(i, m4);
      }
      inst.instanceMatrix.needsUpdate = true;
    },
  };
  return inst;
}

// ---------------------------------------------------------------- 远山背景板（原点：中心）
export function mountainBackdrop(tex, w = 40, h = 20) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }));
  return m;
}

// ---------------------------------------------------------------- 国风剖面小屋（原点：地面中心；正面开口朝 +z，便于看到屋内）
export function cutawayHouse({ w = 7, h = 4.2, d = 5, wall = '#EADFC8', roof = PAL.tile, thick = 0.35 } = {}) {
  const g = new THREE.Group();
  const wm = clay(wall, 0.9);
  const base = box(w + 0.6, 0.35, d + 0.6, clay('#B9AA90', 0.85), 0.05);
  base.position.y = 0.175;
  g.add(base);
  const back = box(w, h, thick, wm, 0.02);
  back.position.set(0, 0.35 + h / 2, -d / 2 + thick / 2);
  const left = box(thick, h, d, wm, 0.02);
  left.position.set(-w / 2 + thick / 2, 0.35 + h / 2, 0);
  const right = left.clone();
  right.position.x = w / 2 - thick / 2;
  g.add(back, left, right);
  // 木柱
  for (const x of [-w / 2 + 0.1, w / 2 - 0.1]) {
    const col = cyl(0.18, 0.2, h, lacquer(PAL.rouge, 0.5), 24);
    col.position.set(x, 0.35 + h / 2, d / 2 - 0.15);
    g.add(col);
  }
  // 瓦屋顶：两坡 + 起翘屋脊
  const roofG = new THREE.Group();
  const slope = 0.5;
  for (const sgn of [-1, 1]) {
    const panel = box(w + 1.6, 0.22, d / 2 / Math.cos(slope) + 0.9, clay(roof, 0.75), 0.06);
    panel.rotation.x = sgn * slope;
    panel.position.set(0, 0.95, sgn * (d / 4 + 0.15));
    roofG.add(panel);
    for (let i = 0; i < 16; i++) {                      // 瓦垄
      const tileRow = cyl(0.07, 0.07, d / 2 / Math.cos(slope) + 0.85, clay(shadeHex(roof, 0.82), 0.7), 8, { cast: false });
      tileRow.rotation.x = Math.PI / 2 + sgn * slope;
      tileRow.position.set(-w / 2 - 0.6 + i * (w + 1.2) / 15, 1.08, sgn * (d / 4 + 0.15));
      roofG.add(tileRow);
    }
  }
  const ridge = box(w + 1.9, 0.3, 0.36, clay(shadeHex(roof, 0.7), 0.7), 0.08);
  ridge.position.y = 1.62;
  roofG.add(ridge);
  for (const sgn of [-1, 1]) {                          // 屋脊两端起翘
    const curl = torus(0.32, 0.1, clay(shadeHex(roof, 0.7), 0.7), Math.PI * 0.9);
    curl.position.set(sgn * (w / 2 + 0.95), 1.9, 0);
    curl.rotation.y = Math.PI / 2;
    curl.rotation.z = sgn > 0 ? 0.2 : Math.PI - 0.2;
    roofG.add(curl);
  }
  roofG.position.y = 0.35 + h;
  g.add(roofG);
  g.userData = { w, h, d, thick, roof: roofG, inner: { x0: -w / 2 + thick, x1: w / 2 - thick, y0: 0.35, y1: 0.35 + h, z0: -d / 2 + thick, z1: d / 2 } };
  return g;
}

export function shadeHex(hex, k) {
  const c = new THREE.Color(hex);
  c.multiplyScalar(k);
  return '#' + c.getHexString();
}

// ---------------------------------------------------------------- 铜钱（方孔圆钱）与钱串柱（原点：底部中心）
let _coinGeo = null;
function coinGeo() {
  if (_coinGeo) return _coinGeo;
  const sh = new THREE.Shape();
  sh.absarc(0, 0, 0.5, 0, Math.PI * 2, false);
  const hole = new THREE.Path();
  hole.moveTo(-0.13, -0.13); hole.lineTo(0.13, -0.13); hole.lineTo(0.13, 0.13); hole.lineTo(-0.13, 0.13); hole.lineTo(-0.13, -0.13);
  sh.holes.push(hole);
  _coinGeo = new THREE.ExtrudeGeometry(sh, { depth: 0.09, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 2, curveSegments: 40 });
  _coinGeo.rotateX(-Math.PI / 2);
  return _coinGeo;
}
export function coin(color = '#C8A15E') {
  return mesh(coinGeo(), metal(color, 0.35));
}
/** 一摞铜钱：userData.set(n) 显示前 n 枚（可为小数，最后一枚从上方落下）。 */
export function coinStack(max = 30, { color = '#C8A15E', seed = 3 } = {}) {
  const g = new THREE.Group();
  const R = rng(seed);
  const coins = [];
  for (let i = 0; i < max; i++) {
    const c = coin(color);
    c.rotation.y = R() * Math.PI;
    c.position.set((R() - 0.5) * 0.05, i * 0.13, (R() - 0.5) * 0.05);
    c.visible = false;
    g.add(c);
    coins.push(c);
  }
  g.userData = {
    coins,
    set(n) {
      for (let i = 0; i < max; i++) {
        const k = clamp01(n - i);
        coins[i].visible = k > 0;
        coins[i].position.y = i * 0.13 + (1 - k) * 1.6;
      }
    },
    height: n => n * 0.13,
  };
  return g;
}

// ---------------------------------------------------------------- 香篆计时（原点：香炉底部；userData.set(燃烧进度 0–1)）
export function incense({ len = 2.2 } = {}) {
  const g = new THREE.Group();
  const burner = mesh(new THREE.CylinderGeometry(0.75, 0.55, 0.6, 40), metal('#6F5A3A', 0.45));
  burner.position.y = 0.3;
  g.add(burner);
  for (let i = 0; i < 3; i++) {
    const leg = cyl(0.07, 0.05, 0.3, metal('#6F5A3A', 0.45), 12);
    const a = i * Math.PI * 2 / 3;
    leg.position.set(Math.cos(a) * 0.45, 0.0, Math.sin(a) * 0.45);
    g.add(leg);
  }
  const ash = cyl(0.62, 0.62, 0.04, clay('#CFC6B8', 0.95), 40, { cast: false });
  ash.position.y = 0.6;
  g.add(ash);
  const stick = cyl(0.035, 0.035, 1, clay('#8C3B2A', 0.8), 10);
  g.add(stick);
  const ember = sphere(0.06, glow('#FF7A3A', 2.0), { cast: false });
  g.add(ember);
  const smoke = [];
  for (let i = 0; i < 8; i++) {
    const s = sphere(0.12, new THREE.MeshBasicMaterial({ color: '#BDB6AA', transparent: true, opacity: 0.25, depthWrite: false }), { cast: false, receive: false });
    g.add(s);
    smoke.push(s);
  }
  g.userData = {
    set(k, t = 0) {
      const l = Math.max(0.02, len * (1 - clamp01(k)));
      stick.scale.y = l;
      stick.position.y = 0.62 + l / 2;
      ember.position.y = 0.62 + l;
      ember.material.emissiveIntensity = 1.6 + 0.6 * Math.sin(t * 9);
      smoke.forEach((s, i) => {
        const u = ((t * 0.35 + i / smoke.length) % 1);
        s.position.set(Math.sin(u * 6 + i) * 0.25 * u, 0.62 + l + u * 2.2, Math.cos(u * 5 + i) * 0.1);
        s.scale.setScalar(0.6 + u * 2.2);
        s.material.opacity = 0.28 * Math.sin(Math.PI * u);
      });
    },
  };
  g.userData.set(0, 0);
  return g;
}

// ---------------------------------------------------------------- 3D 折线图（原点：坐标原点；竹竿坐标轴 + 管状曲线，按进度描出）
/** series: [{pts:[[x,y],...] (0–1 归一化), color, width}]；userData.set(i, p) 描出第 i 条曲线到进度 p。 */
export function lineChart3D({ w = 7, h = 4, series = [], axis = PAL.bamboo } = {}) {
  const g = new THREE.Group();
  const ax = cyl(0.07, 0.07, w + 0.4, clay(axis, 0.6), 12);
  ax.rotation.z = Math.PI / 2;
  ax.position.set(w / 2, 0, 0);
  const ay = cyl(0.07, 0.07, h + 0.4, clay(axis, 0.6), 12);
  ay.position.set(0, h / 2, 0);
  g.add(ax, ay);
  for (let i = 1; i <= 4; i++) {                       // 竹节
    const n = torus(0.085, 0.025, clay(shadeHex(axis, 0.75), 0.6));
    n.rotation.y = Math.PI / 2;
    n.position.set(w * i / 4.4, 0, 0);
    g.add(n);
    const m = torus(0.085, 0.025, clay(shadeHex(axis, 0.75), 0.6));
    m.rotation.x = Math.PI / 2;
    m.position.set(0, h * i / 4.4, 0);
    g.add(m);
  }
  const lines = series.map(sr => {
    const pts = sr.pts.map(([x, y]) => new THREE.Vector3(x * w, y * h, 0.05));
    const curve = new THREE.CatmullRomCurve3(pts, false, sr.smooth === false ? 'catmullrom' : 'centripetal', sr.smooth === false ? 0.02 : 0.5);
    const geo = new THREE.TubeGeometry(curve, Math.max(64, pts.length * 24), sr.width || 0.09, 10, false);
    const m = mesh(geo, glow(sr.color || PAL.cinnabar, 0.25));
    m.geometry.setDrawRange(0, 0);
    g.add(m);
    const head = sphere((sr.width || 0.09) * 1.8, glow(sr.color || PAL.cinnabar, 0.6), { cast: false });
    g.add(head);
    return { m, curve, head, count: geo.index.count };
  });
  g.userData = {
    lines, w, h,
    set(i, p) {
      const L = lines[i];
      const k = clamp01(p);
      const segs = Math.floor(L.count / 60) * 60;
      L.m.geometry.setDrawRange(0, Math.floor(segs * k / 60) * 60);
      const pt = L.curve.getPointAt(Math.max(0.0001, k));
      L.head.position.copy(pt);
      L.head.visible = k > 0.001 && k < 0.999;
    },
  };
  lines.forEach((_, i) => g.userData.set(i, 0));
  return g;
}

// ---------------------------------------------------------------- 冷气流（从出风口向下卷出的半透明带；userData.set(强度, t)）
export function coldAir({ n = 7, color = PAL.cold, len = 3.2, spread = 2.4 } = {}) {
  const g = new THREE.Group();
  const R = rng(9);
  const ribbons = [];
  for (let i = 0; i < n; i++) {
    const x = (i / (n - 1) - 0.5) * spread;
    const pts = [];
    for (let k = 0; k <= 12; k++) {
      const u = k / 12;
      pts.push(new THREE.Vector3(x + Math.sin(u * 3 + i) * 0.15, -u * len, u * len * 0.55 + Math.sin(u * 4 + R() * 6) * 0.1));
    }
    const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, 0.05, 6, false);
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.5, depthWrite: false }));
    m.geometry.setDrawRange(0, 0);
    g.add(m);
    ribbons.push({ m, count: geo.index.count, phase: R() });
  }
  g.userData = {
    set(k, t) {
      ribbons.forEach(r => {
        const u = ((t * 0.6 + r.phase) % 1);
        const head = Math.floor(r.count * clamp01(0.25 + u) / 6) * 6;
        r.m.geometry.setDrawRange(0, Math.floor(head * clamp01(k) / 6) * 6);
        r.m.material.opacity = 0.55 * clamp01(k) * (1 - 0.6 * u);
      });
    },
  };
  return g;
}

// ---------------------------------------------------------------- 匾额（原点：中心；黑底金字或朱底白字）
export function plaque(text, { w = 6, h = 1.8, bg = '#2A2622', fg = '#E2C27A', font = 'MaShanZheng', size = 320 } = {}) {
  const g = new THREE.Group();
  const frame = box(w + 0.4, h + 0.4, 0.3, lacquer(PAL.rouge, 0.4), 0.08);
  g.add(frame);
  const face = textPlane(text, { w, h, px: 512, size, color: fg, bg, font });
  face.position.z = 0.16;
  g.add(face);
  return g;
}

// ---------------------------------------------------------------- 竹简（原点：中心；items 每条一片，userData.set(展开进度, 每片点亮)）
export function bambooSlips(items, { slipW = 0.62, slipH = 5.2, font = 'NotoSerifSC', size = 92 } = {}) {
  const g = new THREE.Group();
  const n = items.length;
  const slips = items.map((txt, i) => {
    const s = new THREE.Group();
    const wood = box(slipW, slipH, 0.08, clay(i % 2 ? '#D8B983' : '#D2B07A', 0.75), 0.04);
    s.add(wood);
    const tex = canvasTex(160, 1344, (c) => {
      c.fillStyle = '#2A2622';
      c.font = `900 ${size}px "${font}"`;
      c.textAlign = 'center'; c.textBaseline = 'top';
      [...txt].forEach((ch, j) => c.fillText(ch, 80, 40 + j * (size * 1.12)));
    });
    const face = new THREE.Mesh(new THREE.PlaneGeometry(slipW * 0.9, slipH * 0.96), new THREE.MeshBasicMaterial({ map: tex, transparent: true }));
    face.position.z = 0.045;
    s.add(face);
    g.add(s);
    return s;
  });
  for (const yy of [-slipH * 0.32, slipH * 0.32]) {
    const cord = cyl(0.02, 0.02, n * (slipW + 0.08) + 0.4, clay('#6B4A2E', 0.8), 6, { cast: false });
    cord.rotation.z = Math.PI / 2;
    cord.position.set(0, yy, 0.06);
    g.add(cord);
  }
  g.userData = {
    slips,
    /** 自右向左展开（传统竖排顺序）：k 为展开进度，未展开的片叠在右侧 */
    set(k) {
      slips.forEach((s, i) => {
        const target = ((n - 1) / 2 - i) * (slipW + 0.08);
        const q = clamp01(k * n - i);
        s.position.x = lerp((n - 1) / 2 * (slipW + 0.08), target, q);
        s.rotation.y = (1 - q) * -0.6;
        s.visible = q > 0 || i === 0;
      });
    },
  };
  g.userData.set(1);
  return g;
}

// ---------------------------------------------------------------- 泥人角色（原点：脚底中心，面朝 +z；userData.pose({walk, armL, armR, nod})）
export function clayFigure({ color = PAL.azure, skin = '#F1D2B2', hat = null, s = 1 } = {}) {
  const g = new THREE.Group();
  const body = mesh(new THREE.CapsuleGeometry(0.42 * s, 0.7 * s, 8, 24), clay(color, 0.75));
  body.position.y = 1.35 * s;
  g.add(body);
  const robe = mesh(new THREE.CylinderGeometry(0.45 * s, 0.62 * s, 0.7 * s, 32), clay(shadeHex(color, 0.85), 0.75));
  robe.position.y = 0.85 * s;
  g.add(robe);
  const head = new THREE.Group();
  const face = sphere(0.36 * s, clay(skin, 0.7));
  head.add(face);
  for (const x of [-0.12, 0.12]) {
    const eye = sphere(0.045 * s, clay(PAL.ink, 0.5), { cast: false });
    eye.position.set(x * s, 0.04 * s, 0.33 * s);
    head.add(eye);
  }
  const cheekMat = new THREE.MeshBasicMaterial({ color: '#E89A8A', transparent: true, opacity: 0.55 });
  for (const x of [-0.2, 0.2]) {
    const ch = new THREE.Mesh(new THREE.CircleGeometry(0.06 * s, 16), cheekMat);
    ch.position.set(x * s, -0.08 * s, 0.335 * s);
    head.add(ch);
  }
  const hair = mesh(new THREE.SphereGeometry(0.37 * s, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.45), clay(PAL.ink, 0.8));
  hair.rotation.x = -0.25;
  head.add(hair);
  if (hat === 'bun') {
    const bun = sphere(0.14 * s, clay(PAL.ink, 0.8));
    bun.position.set(0, 0.36 * s, -0.08 * s);
    head.add(bun);
  } else if (hat === 'douli') {
    const dl = mesh(new THREE.ConeGeometry(0.75 * s, 0.32 * s, 40), clay('#C9A86A', 0.85));
    dl.position.y = 0.34 * s;
    head.add(dl);
  }
  head.position.y = 2.15 * s;
  g.add(head);
  const limb = (r, l, mat) => {
    const p = new THREE.Group();
    const m = mesh(new THREE.CapsuleGeometry(r, l, 6, 16), mat);
    m.position.y = -l / 2 - r;
    p.add(m);
    return p;
  };
  const armL = limb(0.11 * s, 0.55 * s, clay(color, 0.75));
  const armR = limb(0.11 * s, 0.55 * s, clay(color, 0.75));
  armL.position.set(-0.5 * s, 1.72 * s, 0);
  armR.position.set(0.5 * s, 1.72 * s, 0);
  const legL = limb(0.13 * s, 0.32 * s, clay(PAL.ink2, 0.8));
  const legR = limb(0.13 * s, 0.32 * s, clay(PAL.ink2, 0.8));
  legL.position.set(-0.2 * s, 0.62 * s, 0);
  legR.position.set(0.2 * s, 0.62 * s, 0);
  g.add(armL, armR, legL, legR);
  g.userData = {
    head, armL, armR, legL, legR,
    /** walk：步态相位（每 1.0 一步，0 为站立）；armL/armR：抬臂角度（弧度，正值向前上抬）；nod：点头 */
    pose({ walk = 0, amp = 0, armL: aL = 0, armR: aR = 0, nod = 0, tilt = 0 } = {}) {
      const sw = Math.sin(walk * Math.PI) * amp;
      legL.rotation.x = sw * 0.6;
      legR.rotation.x = -sw * 0.6;
      armL.rotation.x = -sw * 0.5 - aL;
      armR.rotation.x = sw * 0.5 - aR;
      armL.rotation.z = -0.12 - (aL > 0 ? 0.1 : 0);
      armR.rotation.z = 0.12 + (aR > 0 ? 0.1 : 0);
      head.rotation.x = nod;
      head.rotation.z = tilt;
      g.children.forEach(ch => { if (ch.userData.base === undefined) ch.userData.base = ch.position.y;
        ch.position.y = ch.userData.base + Math.abs(Math.sin(walk * Math.PI)) * 0.06 * amp * s; });
    },
  };
  g.userData.pose();
  return g;
}
