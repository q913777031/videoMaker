// 镜 10 longaway · 11 toggle · 12 surge · 13 fixed · 14 conclusion · 15 credits
import { THREE, PAL, TL, makeCamera, camKeys, at, cue, prog, easeOut, easeIn, easeInOut, clamp01, lerp, pulse, shake, inkSplash,
  toScreen, box, cyl, sphere, torus, clay, lacquer, metal, glow } from '../engine.js';
import { incense, remote, scroll, acOutdoor, coin, lineChart3D, plaque, lantern, bambooSlips, clayFigure } from '../props.js';
import { boatScene, boatRig, tagLabel, followPt, follow, FRONT, figureOnStone, pierAt } from './boatkit.js';
import { paperStage } from './s07_09_evidence.js';

const OUTER = 0.15, LOW = -1.6;

// ---------------------------------------------------------------- 镜 10：离开几个小时
export function longaway({ ui }) {
  const W = boatScene();
  const rig = boatRig(W.scene, {});
  const pier = pierAt(W.scene, 3.5, -4.4, { ghost: true });
  const inc = incense({ len: 2.4 });
  at(inc, -3.4, 0.9, -4.4, 0, 0.8);
  const stone = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.1, 6, 9), new THREE.MeshStandardMaterial({ color: '#8E8A80', roughness: 0.9 }));
  stone.position.set(-3.4, -2.1, -4.4);
  W.scene.add(inc, stone);
  ui.sealStamp('seal', '省', { top: '700px' });
  tagLabel(ui, 'ghost', '一直开要花的', PAL.ink2);
  const t0 = cue('longaway.time_lapse'), tBack = cue('longaway.return_pump'), tGhost = cue('longaway.ghost_column');
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: FRONT.pos, look: FRONT.look, fov: FRONT.fov }, { t: 2.1, pos: [1.8, 2.8, 22], look: [1.2, -0.6, -3], fov: 33 },
        { t: 4.2, pos: [3.0, 3.0, 17], look: [3.0, 1.0, -4.4], fov: 32 }]);
      W.tick(t, OUTER);
      W.clouds.forEach((c, i) => { c.position.x = -14 + ((lt * 6 + i * 13) % 28); });
      inc.userData.set(easeInOut(prog(t, t0, (tBack - t0) * 0.95)), t);
      const fill = easeOut(prog(t, t0, tBack - t0));
      const inner = t < tBack ? lerp(LOW, OUTER - 0.12, fill) : lerp(OUTER - 0.12, -0.8, easeInOut(prog(t, tBack, 2.2)));
      rig.set(t, { outer: OUTER, inner, pump: Math.max(0, t - tBack) * 4, flow: t > tBack ? 1 : 0, blur: t > tBack ? 0.6 : 0,
        soak: t < tBack ? fill : 1 - prog(t, tBack, 2) });
      rig.boat.userData.ac.userData.set(t > tBack ? 1 : 0, t > tBack ? '26°' : '', t > tBack);
      const n = t < tBack ? 6 : 6 + Math.min(9, (t - tBack) / 0.18);
      pier.userData.set(n, 6 + 20 * easeOut(prog(t, tBack, 1.0)));
      ui.stamp('seal', t - tGhost, { x: 0, y: 0 });
      followPt(ui, 'ghost', W.camera, [4.8, 4.4, -4.4], easeOut(prog(t, tBack + 0.4, 0.4)));
    },
    fx(g, lt, t) { inkSplash(g, 540, 700, t - tGhost, 200, PAL.cinnabar, 71, 0.7); },
  };
}

// ---------------------------------------------------------------- 镜 11：几分钟一开关
function lock() {
  const g = new THREE.Group();
  g.add(box(0.5, 0.42, 0.18, metal('#C8A15E', 0.35), 0.05));
  const sh = torus(0.17, 0.05, metal('#C8A15E', 0.35), Math.PI);
  sh.position.y = 0.2;
  g.add(sh);
  return g;
}
export function toggle({ ui }) {
  const W = boatScene();
  const A = boatRig(W.scene, { x: -2.5, B: 3.0, seaW: 1.0, ac: false });
  const Bt = boatRig(W.scene, { x: 2.5, B: 3.0, seaW: 1.0, ac: false });
  const pA = pierAt(W.scene, -2.5, -9.5, { top: 1.0, seed: 6 });
  const pB = pierAt(W.scene, 2.5, -9.5, { top: 1.0, seed: 7 });
  const lk = lock();
  W.scene.add(lk);
  tagLabel(ui, 'na', '一直开', PAL.jade);
  tagLabel(ui, 'nb', '几分钟开关一次', PAL.cinnabar);
  tagLabel(ui, 'lock', '约 3 分钟重启保护', PAL.ochre);
  const t0 = cue('toggle.toggle_off'), t1 = cue('toggle.lock_wait'), t2 = cue('toggle.columns_equal');
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: [3.4, 1.6, 15], look: [2.5, -0.4, -2], fov: 33 }, { t: 1.6, pos: [3.4, 1.6, 15], look: [2.5, -0.4, -2], fov: 33 },
        { t: 2.3, pos: [0, 3.4, 26], look: [0, -0.4, -4], fov: 34 }]);
      W.tick(t, OUTER);
      A.set(t, { outer: OUTER, inner: LOW, pump: t * 1.6, flow: 1 });
      const stopped = (t > t0 && t < t1 + 0.9) || t > t1 + 1.9;
      const innerB = LOW + 0.5 * easeOut(prog(t, t0, 1.2)) - 0.2 * easeInOut(prog(t, t1 + 0.9, 0.8)) + 0.2 * easeOut(prog(t, t1 + 1.9, 1));
      Bt.set(t, { outer: OUTER, inner: innerB, pump: stopped ? t0 * 1.6 : t * 2.4, flow: stopped ? 0 : 1 });
      // 铜锁：扣在右船链条上，第 2 拍后晃三下松开
      Bt.wheel.updateWorldMatrix(true, true);
      const wp = Bt.wheel.getWorldPosition(new THREE.Vector3());
      lk.position.set(wp.x + 1.4, wp.y + 1.6 + (t > t1 + 0.9 ? (t - t1 - 0.9) * 3 : 0), wp.z + 0.4);
      lk.rotation.z = t > t1 ? 0.35 * Math.sin((t - t1) * 14) * Math.exp(-(t - t1) * 1.5) : 0.1 * pulse(t, t0, 6, 30);
      lk.visible = t > t0 && t < t1 + 1.3;
      lk.scale.setScalar(easeOut(prog(t, t0, 0.12)));
      const k = clamp01(lt / (t2 - (t - lt)));
      pA.userData.set(k * 16);
      pB.userData.set(k * 16);
      const o = easeOut(prog(lt, 0.1, 0.4));
      followPt(ui, 'na', W.camera, [A.root.position.x, 3.2, -6], easeOut(prog(t, t1 + 0.6, 0.4)));
      followPt(ui, 'nb', W.camera, [Bt.root.position.x, 3.2, -6], o);
      followPt(ui, 'lock', W.camera, [wp.x + 1.4, wp.y + 2.4, wp.z + 0.4], lk.visible ? easeOut(prog(t, t0 + 0.1, 0.3)) : 0);
    },
  };
}

// ---------------------------------------------------------------- 镜 12：“开机那下最费电？”
export function surge({ ui }) {
  const { scene } = paperStage({ mtn: 14 });
  const sc = scroll('开机那下最费电？', { w: 6.4, h: 1.7, size: 150 });
  at(sc, 0, 5.6, -1);
  scene.add(sc);
  const out = acOutdoor({ s: 1.1 });
  at(out, -2.2, 0, 0.5, 0.35);
  scene.add(out);
  const spark = new THREE.Mesh(new THREE.SphereGeometry(0.5, 24, 16), glow('#FFB25A', 3));
  spark.position.set(-1.6, 1.9, 1.2);
  scene.add(spark);
  const small = coin();
  small.scale.setScalar(0.8);
  scene.add(small);
  const tall = [];
  for (let i = 0; i < 26; i++) { const c = coin(); c.position.set(2.6, i * 0.13, 0.2); c.rotation.y = i; scene.add(c); tall.push(c); }
  ui.sealStamp('wu', '误', { top: '540px' });
  tagLabel(ui, 's1', '启动冲击：一瞬间', PAL.ochre);
  tagLabel(ui, 's2', '把热屋子压回设定温度', PAL.cinnabar);
  const camera = makeCamera(36);
  const tScroll = cue('surge.scroll_open'), tSpark = cue('surge.spark'), tSeal = cue('surge.stamp_wrong'), tPull = cue('surge.long_pull');
  return {
    scene, camera,
    update(lt, t) {
      camKeys(camera, lt, [{ t: 0, pos: [-0.6, 3.2, 17], look: [-0.6, 2.4, 0], fov: 36 }, { t: 2.2, pos: [-0.6, 3.2, 17], look: [-0.6, 2.4, 0], fov: 36 },
        { t: 3.6, pos: [0.3, 3.0, 23], look: [0.3, 1.6, 0], fov: 36 }]);
      shake(camera, t, tSeal, 0.15);
      sc.userData.set(easeOut(prog(t, tScroll, 0.5)));
      out.userData.fan.rotation.z = -t * 9;
      const sk = t - tSpark;
      spark.visible = sk > 0 && sk < 0.22;
      spark.scale.setScalar(1 + sk * 6);
      small.visible = sk > 0;
      small.position.set(-0.4, Math.max(0, 1.8 - sk * sk * 14) + Math.max(0, pulse(t, tSpark + 0.36, 9, 22)) * 0.15, 1.6);
      const n = clamp01((t - tPull) / 1.6) * 26;
      tall.forEach((c, i) => { c.visible = i < n; });
      ui.stamp('wu', t - tSeal, { x: 0, y: 0, r: -8 });
      followPt(ui, 's1', camera, [-0.4, 1.7, 1.6], easeOut(prog(t, tSpark + 0.3, 0.3)));
      followPt(ui, 's2', camera, [2.6, 4.0, 0.2], easeOut(prog(t, tPull + 0.6, 0.4)));
    },
    fx(g, lt, t) { inkSplash(g, 540, 540, t - tSeal, 200, PAL.cinnabar, 81, 0.6); },
  };
}

// ---------------------------------------------------------------- 镜 13：定频机自己开停
export function fixed({ ui }) {
  const W = boatScene();
  const rig = boatRig(W.scene, {});
  const sq = lineChart3D({ w: 3.4, h: 1.4, series: [{ pts: [[0, 0.95], [0.18, 0.95], [0.19, 0.05], [0.38, 0.05], [0.39, 0.95], [0.58, 0.95],
    [0.59, 0.05], [0.78, 0.05], [0.79, 0.95], [1, 0.95]], color: PAL.cinnabar, width: 0.06, smooth: false }] });
  sq.position.set(-5.6, 2.0, -7.5);
  W.scene.add(sq);
  tagLabel(ui, 'chart', '压缩机：全速 / 停', PAL.cinnabar);
  tagLabel(ui, 'fx', '定频机 · 遥控器一直开着', PAL.ink2);
  const t0 = cue('fixed.lever_stop'), t1 = cue('fixed.lever_go'), t2 = cue('fixed.share_column');
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: [1.2, 2.6, 23], look: [0.2, -0.6, -3], fov: 34 }, { t: 2.1, pos: [-1.2, 2.8, 22], look: [-1.6, 0.0, -4], fov: 34 }]);
      W.tick(t, OUTER);
      // 遥控器一直开（指示灯常亮），压缩机却自己全速 / 停 循环
      const on = (t < t0) || (t > t1 && t < t1 + 0.9) || t > t1 + 1.8;
      const inner = LOW + 0.18 * (on ? 0 : 1) * 0.5;
      rig.set(t, { outer: OUTER, inner, pump: on ? t * 1.8 : t0 * 1.8, flow: on ? 1 : 0 });
      rig.boat.userData.ac.userData.set(1, '26°', true);
      sq.userData.set(0, clamp01(lt / 4.0));
      followPt(ui, 'chart', W.camera, [-3.9, 4.0, -7.5], easeOut(prog(lt, 0.4, 0.4)));
      followPt(ui, 'fx', W.camera, [0, 3.2, -6.8], easeOut(prog(lt, 0.1, 0.4)));
    },
  };
}

// ---------------------------------------------------------------- 镜 14：结论匾额
export function conclusion({ ui }) {
  const W = boatScene();
  const A = boatRig(W.scene, { x: -2.5, B: 3.0, seaW: 1.0, ac: false });
  const Bt = boatRig(W.scene, { x: 2.5, B: 3.0, seaW: 1.0, ac: false });
  const pl = plaque('不是一刀切', { w: 5.4, h: 1.5, size: 260 });
  W.scene.add(pl);
  const lans = [];
  for (const x of [-5.2, -4.2, 4.2, 5.2]) { const l = lantern(0.7); at(l, x, 6.2 + (Math.abs(x) > 5 ? -0.4 : 0), -3); W.scene.add(l); lans.push(l); }
  tagLabel(ui, 'a', '短出门：开着', PAL.jade);
  tagLabel(ui, 'b', '离开久：关掉', PAL.cinnabar);
  const t0 = cue('conclusion.plaque_drop'), t1 = cue('conclusion.two_boats'), t2 = cue('conclusion.lanterns');
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: [0, 2.2, 22], look: [0, 4.0, -3], fov: 36 }, { t: 2.0, pos: [0, 3.2, 26], look: [0, 0.2, -3.5], fov: 36 }]);
      shake(W.camera, t, t0, 0.3);
      W.tick(t, OUTER);
      pl.position.set(0, lerp(14, 5.6, easeIn(prog(t, t0 - 0.3, 0.3))) + 0.06 * pulse(t, t0, 6, 20), -3);
      A.set(t, { outer: OUTER, inner: LOW, pump: t * 1.0, flow: 0.7 });
      const fold = easeInOut(prog(t, t1, 1.0));
      Bt.set(t, { outer: OUTER, inner: lerp(LOW, -0.6, fold), pump: 0, flow: 0 });
      Bt.wheel.scale.y = Math.max(0.02, 1 - fold);
      lans.forEach((l, i) => {
        const k = easeOut(prog(t, t2 + i * 0.12, 0.3));
        l.children[0].material.emissive = new THREE.Color(PAL.cinnabar);
        l.children[0].material.emissiveIntensity = 0.9 * k;
        l.rotation.z = Math.sin(t * 2 + i) * 0.05;
      });
      followPt(ui, 'a', W.camera, [-2.5, 2.6, -5], easeOut(prog(t, t1, 0.4)));
      followPt(ui, 'b', W.camera, [2.5, 2.6, -5], easeOut(prog(t, t1, 0.4)));
    },
    fx(g, lt, t) {
      const [x, y] = toScreen(pl, W.camera);
      inkSplash(g, x, y, t - t0, 340, PAL.ink, 91, 0.8);
    },
  };
}

// ---------------------------------------------------------------- 镜 15：片尾出处
export function credits({ ui, info }) {
  const { scene } = paperStage({ mtn: 16 });
  const sl = bambooSlips(['传热', '水车', '实测', '分界', '机型', '误区'], { slipW: 0.6, slipH: 2.6, size: 100 });
  at(sl, 0, 7.4, -2);
  scene.add(sl);
  const refs = (TL.refs || []).map(r => `<div style="margin:6px 0">${r}</div>`).join('');
  ui.add('refs', `<div style="font:900 44px NotoSerifSC;color:${PAL.ink};margin-bottom:18px">依据与出处</div>
    <div style="font:500 27px/1.5 NotoSansSC;color:${PAL.ink2};width:880px;text-align:center">${refs}</div>`,
  { left: '540px', top: '1060px', opacity: 0, textAlign: 'center' });
  ui.sealStamp('end', '完', { top: '1560px', left: '900px' });
  const camera = makeCamera(36);
  const t0 = cue('credits.slips_unroll'), t1 = cue('credits.seal_turn'), t2 = cue('credits.final_stamp');
  return {
    scene, camera,
    update(lt, t) {
      camKeys(camera, lt, [{ t: 0, pos: [-1.5, 6.2, 15], look: [0, 5.0, -2], fov: 36 }, { t: 4.2, pos: [1.0, 6.0, 15], look: [0, 5.0, -2], fov: 36 }]);
      shake(camera, t, t2, 0.12);
      sl.userData.set(easeOut(prog(t, t0, 1.2)));
      ui.set('refs', { o: easeOut(prog(t, t0 + 0.4, 0.6)), x: 0, y: 0 });
      ui.stamp('end', t - t2, { x: 0, y: 0, r: -8 });
    },
    fx(g, lt, t) { inkSplash(g, 900, 1560, t - t2, 130, PAL.cinnabar, 101, 0.6); },
  };
}
