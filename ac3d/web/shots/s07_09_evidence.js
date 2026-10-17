// 镜 7 balance：天平称“少渗的热”与“猛车多花的电”，看离开多久往哪头歪。
// 镜 8 jiangsu：两条船对照（江苏电科院实测）。镜 9 threshold：三炷香的分界点不固定。
import { THREE, PAL, lights, makeCamera, camKeys, at, cue, prog, easeOut, easeIn, easeInOut, clamp01, lerp, pulse, shake,
  inkSplash, toScreen, shadowFloor, inkMountainsTex, cloud3d, box, cyl, sphere, torus, clay, lacquer, metal, glow, mesh } from '../engine.js';
import { mountainBackdrop, coin, coinStack, incense, bambooSlips } from '../props.js';
import { boatScene, boatRig, tagLabel, followPt, follow, pierAt } from './boatkit.js';

export function paperStage({ key = [4, 11, 9], mtn = 9 } = {}) {
  const scene = new THREE.Scene();
  lights(scene, { key, intensity: 2.6, shadow: 10 });
  scene.add(shadowFloor(60, 0.24));
  const m = mountainBackdrop(inkMountainsTex(mtn, { tint: '#4A4440' }), 70, 34);
  m.position.set(0, 11, -26);
  scene.add(m);
  const cl = cloud3d(1.3);
  at(cl, -6, 9, -10);
  scene.add(cl);
  return { scene, cloud: cl };
}

// ---------------------------------------------------------------- 天平
function balanceProp() {
  const g = new THREE.Group();
  const post = cyl(0.14, 0.2, 6.2, clay(PAL.wood, 0.6), 18);
  post.position.y = 3.1;
  const foot = box(2.4, 0.3, 1.6, clay(PAL.wood, 0.6), 0.08);
  foot.position.y = 0.15;
  g.add(post, foot);
  const arm = new THREE.Group();
  arm.position.y = 6.2;
  const beam = cyl(0.09, 0.09, 7.2, lacquer('#2A2622', 0.4), 18);
  beam.rotation.z = Math.PI / 2;
  arm.add(beam);
  const knob = sphere(0.26, metal('#C8A15E', 0.35));
  arm.add(knob);
  const pans = [];
  for (const side of [-1, 1]) {
    const hang = new THREE.Group();
    hang.position.x = side * 3.4;
    for (let i = 0; i < 3; i++) {
      const c = cyl(0.012, 0.012, 2.2, clay(PAL.ink, 0.8), 6, { cast: false });
      const a = i * Math.PI * 2 / 3;
      c.position.set(Math.cos(a) * 0.4, -1.1, Math.sin(a) * 0.4);
      c.rotation.z = Math.cos(a) * 0.18;
      c.rotation.x = -Math.sin(a) * 0.18;
      hang.add(c);
    }
    const dish = mesh(new THREE.CylinderGeometry(0.95, 0.7, 0.16, 40), metal('#B58A4E', 0.4));
    dish.position.y = -2.25;
    hang.add(dish);
    arm.add(hang);
    pans.push(hang);
  }
  g.add(arm);
  g.userData = {
    arm, pans,
    set(tilt) {
      arm.rotation.z = tilt;
      pans.forEach(p => { p.rotation.z = -tilt; });
    },
  };
  return g;
}

export function balance({ ui }) {
  const { scene } = paperStage();
  const bal = balanceProp();
  at(bal, 0, 0, 0);
  scene.add(bal);
  // 左盘：凝住的橙色水珠（关掉少渗的热）；右盘：铜钱（重开猛车多花的电）
  const drops = [];
  for (let i = 0; i < 14; i++) {
    const d = sphere(0.22, glow('#FF8A3D', 0.5));
    bal.userData.pans[0].add(d);
    drops.push(d);
  }
  const coins = [];
  for (let i = 0; i < 6; i++) {
    const c = coin();
    c.scale.setScalar(0.9);
    bal.userData.pans[1].add(c);
    coins.push(c);
  }
  const sticks = [];
  for (let i = 0; i < 5; i++) {
    const s = incense({ len: 1.6 });
    at(s, -2.2 + i * 1.1, 0, -2.6, 0, 0.55);
    scene.add(s);
    sticks.push(s);
  }
  tagLabel(ui, 'l', '关掉：少渗的热', PAL.vermilion);
  tagLabel(ui, 'r', '重开：猛车多花的电', PAL.ochre);
  tagLabel(ui, 'time', '线香 = 离开时长', PAL.ink2);
  const camera = makeCamera(36);
  const tSlam = cue('balance.scale_slam'), tFill = cue('balance.pans_fill'), tShort = cue('balance.short_stick'), tLong = cue('balance.long_stick');
  return {
    scene, camera,
    update(lt, t) {
      camKeys(camera, lt, [{ t: 0, pos: [0, 3.4, 27], look: [0, 2.6, 0], fov: 36 }, { t: 4.3, pos: [0, 3.4, 27], look: [0, 2.6, 0], fov: 36 },
        { t: 8.5, pos: [7.5, 4.2, 25], look: [0, 2.6, 0], fov: 36 }]);
      shake(camera, t, tSlam, 0.3);
      const fall = easeIn(prog(t, tSlam - 0.3, 0.3));
      bal.position.y = lerp(9, 0, fall);
      // 盘里物件：第 4 拍各落几枚
      const nd = t < tFill ? 0 : Math.min(6, (t - tFill) / 0.25) + (t > tLong ? Math.min(8, (t - tLong) / 0.12) : 0);
      drops.forEach((d, i) => {
        d.visible = i < nd;
        d.position.set(((i * 37) % 7 - 3) * 0.17, -2.0 + Math.floor(i / 6) * 0.3, ((i * 53) % 5 - 2) * 0.17);
      });
      const nc = t < tFill ? 0 : Math.min(4, (t - tFill) / 0.3) + (t > tShort ? Math.min(2, (t - tShort) / 0.2) : 0);
      coins.forEach((c, i) => { c.visible = i < nc; c.position.set((i % 2 - 0.5) * 0.2, -2.12 + i * 0.13, 0); });
      // 倾斜：摆动 → 短时离开略偏右（几乎持平）→ 长时离开重重偏左
      let tilt = 0.22 * pulse(t, tSlam, 2.2, 6);
      tilt += -0.06 * easeOut(prog(t, tShort - 0.2, 0.2)) + 0.01 * pulse(t, tShort, 6, 22);
      tilt += 0.36 * easeIn(prog(t, tLong - 0.25, 0.25)) - 0.03 * pulse(t, tLong, 5, 20);
      bal.userData.set(tilt);
      sticks.forEach((s, i) => {
        const k = i === 0 ? 0.35 * prog(t, tShort - 0.5, 0.5) : 0.35 * prog(t, tShort - 0.5, 0.5) * 0;
        const burn = Math.max(i === 0 ? k : 0, easeInOut(prog(t, tLong - 1.0, 1.0)) * 0.95);
        s.userData.set(burn, t);
      });
      follow(ui, 'l', bal.userData.pans[0], camera, [0, -3.0, 0], easeOut(prog(t, tFill, 0.4)));
      follow(ui, 'r', bal.userData.pans[1], camera, [0, -3.0, 0], easeOut(prog(t, tFill, 0.4)));
      followPt(ui, 'time', camera, [0, 1.9, -2.6], easeOut(prog(t, tShort - 0.6, 0.4)));
    },
    fx(g, lt, t) {
      const [x, y] = toScreen(bal, camera, [0, 6.2, 0]);
      inkSplash(g, x, y, t - tSlam, 300, PAL.ink, 51, 0.8);
      const [x2, y2] = toScreen(bal.userData.pans[0], camera, [0, -2.2, 0]);
      inkSplash(g, x2, y2, t - tLong, 160, PAL.vermilion, 53, 0.7);
    },
  };
}

// ---------------------------------------------------------------- 江苏对照实验：两条船
export function jiangsu({ ui }) {
  const W = boatScene();
  const A = boatRig(W.scene, { x: -2.5, B: 3.0, seaW: 1.0, ac: false });
  const Bt = boatRig(W.scene, { x: 2.5, B: 3.0, seaW: 1.0, ac: false });
  tagLabel(ui, 'na', '一直开', PAL.jade);
  tagLabel(ui, 'nb', '关 10 分钟再开', PAL.cinnabar);
  const pA = pierAt(W.scene, -2.5, -9.5, { top: 1.0, seed: 4 });
  const pB = pierAt(W.scene, 2.5, -9.5, { top: 1.0, seed: 5 });
  tagLabel(ui, 'a', '0.445 度', PAL.jade);
  tagLabel(ui, 'b', '0.456 度', PAL.cinnabar);
  tagLabel(ui, 'dur', '同样 45 分钟', PAL.ink2);
  const tIn = cue('jiangsu.boats_glide'), tPause = cue('jiangsu.right_pause'), tRush = cue('jiangsu.right_rush'), tTie = cue('jiangsu.columns_tie');
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: [0, 3.4, 26], look: [0, -0.8, -3.5], fov: 34 }, { t: 4.3, pos: [0, 3.4, 26], look: [0, -0.8, -3.5], fov: 34 },
        { t: 6.3, pos: [0, 4.6, 22], look: [0, 1.4, -9.5], fov: 32 }]);
      W.tick(t, 0.15);
      const glide = easeOut(prog(t, tIn - 0.5, 0.5));
      A.root.position.x = lerp(-9, -2.5, glide);
      Bt.root.position.x = lerp(9, 2.5, glide);
      const run = t * 1.6;
      A.set(t, { outer: 0.15, inner: -1.6, pump: run, flow: 1 });
      // 右船：第 4 拍刹停、船内水位上升；第 6 拍恢复并加速
      const paused = t > tPause && t < tRush;
      const innerB = -1.6 + 0.45 * easeOut(prog(t, tPause, 1.0)) - 0.45 * easeInOut(prog(t, tRush, 1.8));
      const pumpB = t < tPause ? run : t < tRush ? tPause * 1.6 : tPause * 1.6 + (t - tRush) * 2.8;
      Bt.set(t, { outer: 0.15, inner: innerB, pump: pumpB, flow: paused ? 0 : 1, blur: t > tRush ? 0.5 : 0 });
      // 钱串柱：到第 8 拍几乎一样高（0.445 vs 0.456）
      const k = clamp01((t - tIn) / (tTie - tIn));
      pA.userData.set(k * 22);
      pB.userData.set(t < tPause ? k * 22 : t < tRush ? (tPause - tIn) / (tTie - tIn) * 22 : lerp((tPause - tIn) / (tTie - tIn) * 22, 22.6, clamp01((t - tRush) / (tTie - tRush))));
      const lo = easeOut(prog(t, tTie, 0.25));
      followPt(ui, 'a', W.camera, [-2.5, 4.3, -9.5], lo);
      followPt(ui, 'b', W.camera, [2.5, 4.3, -9.5], lo);
      followPt(ui, 'na', W.camera, [A.root.position.x, 3.2, -6], easeOut(prog(t, tIn, 0.4)));
      followPt(ui, 'nb', W.camera, [Bt.root.position.x, 3.2, -6], easeOut(prog(t, tIn, 0.4)));
      followPt(ui, 'dur', W.camera, [0, 2.4, -2], easeOut(prog(t, tIn + 0.3, 0.4)) * (1 - prog(t, tTie - 0.4, 0.3)));
    },
  };
}

// ---------------------------------------------------------------- 分界点：三炷香
export function threshold({ ui }) {
  const { scene } = paperStage({ mtn: 12 });
  const night = new THREE.Mesh(new THREE.PlaneGeometry(90, 50), new THREE.MeshBasicMaterial({ color: '#1F2738', transparent: true, opacity: 0, depthWrite: false }));
  night.position.set(0, 12, -27);
  scene.add(night);
  const moon = new THREE.Mesh(new THREE.CircleGeometry(1.4, 40), new THREE.MeshBasicMaterial({ color: '#F2E4C4', transparent: true, opacity: 0 }));
  moon.position.set(5, 15, -26);
  const sun = new THREE.Mesh(new THREE.CircleGeometry(1.8, 40), new THREE.MeshBasicMaterial({ color: '#D9482B', transparent: true, opacity: 1 }));
  sun.position.set(-5, 15, -26);
  scene.add(moon, sun);
  const LEN = 3.2;
  const marks = [10, 18, 35];                // 分钟
  const sticks = marks.map((m, i) => {
    const s = incense({ len: LEN });
    at(s, (i - 1) * 1.9, 0, 0, 0, 0.9);
    scene.add(s);
    const ring = torus(0.07, 0.025, lacquer(PAL.cinnabar, 0.4));
    ring.rotation.x = Math.PI / 2;
    ring.position.set((i - 1) * 1.9, 0.9 * (0.62 + LEN * (1 - m / 40)), 0);
    scene.add(ring);
    return s;
  });
  const slips = bambooSlips(['气温', '保温', '机型', '设定'], { slipW: 0.7, slipH: 2.4, size: 110 });
  at(slips, 0, 4.9, -4);
  scene.add(slips);
  const names = ['江苏 · 约10分', '大金·夜 · 约18分', '大金·昼 · 约35分'];
  names.forEach((n, i) => tagLabel(ui, 'n' + i, n, [PAL.jade, PAL.azure, PAL.cinnabar][i]));
  tagLabel(ui, 'hint', '超过分界点：关掉更省', PAL.ink2);
  const camera = makeCamera(36);
  const t0 = cue('threshold.sticks_rise'), tJ = cue('threshold.mark_jiangsu'), tN = cue('threshold.mark_night'), tD = cue('threshold.mark_day'), tS = cue('threshold.slips_open');
  return {
    scene, camera,
    update(lt, t) {
      camKeys(camera, lt, [{ t: 0, pos: [0, 12, 9], look: [0, 0.8, 0], fov: 38 }, { t: 4.2, pos: [0, 3.0, 15], look: [0, 1.4, 0], fov: 38 },
        { t: 5.3, pos: [0, 3.4, 16.5], look: [0, 2.0, -1], fov: 38 }]);
      const rise = easeOut(prog(t, t0 - 0.2, 0.2));
      // 每炷香各自烧到自己的朱线：江苏第 4 拍、夜第 6 拍、昼第 8 拍
      [tJ, tN, tD].forEach((tm, i) => {
        sticks[i].position.y = lerp(-3, 0, rise);
        sticks[i].scale.setScalar(0.9);
        const burn = (marks[i] / 40) * clamp01((t - t0) / (tm - t0));
        sticks[i].userData.set(burn, t);
      });
      const nightK = easeInOut(prog(t, tN - 0.4, 0.4)) * (1 - easeInOut(prog(t, tD - 0.4, 0.4)));
      night.material.opacity = 0.55 * nightK;
      moon.material.opacity = nightK;
      sun.material.opacity = 1 - nightK;
      slips.userData.set(easeOut(prog(t, tS, 2.0)));
      slips.visible = t > tS - 0.05;
      [tJ, tN, tD].forEach((tm, i) => followPt(ui, 'n' + i, camera, [(i - 1) * 1.9, (i % 2 ? 4.3 : 3.7), 0], easeOut(prog(t, t0 + 0.3 + i * 0.15, 0.4))));
      followPt(ui, 'hint', camera, [0, -0.6, 1.5], easeOut(prog(t, tD + 0.3, 0.4)));
    },
    fx(g, lt, t) {
      const [x, y] = toScreen(sticks[2], camera, [0, 0.6, 0]);
      inkSplash(g, x, y, t - tD, 120, PAL.ink, 61, 0.6);
    },
  };
}
