// 镜 4 pump / 镜 5 off / 镜 6 restart：水车车水 → 关掉后船里水涨、渗得变慢、船板存热 → 回来猛车积水、效率低。
import { THREE, PAL, camKeys, cue, prog, easeOut, easeIn, easeInOut, clamp01, lerp, pulse, shake, inkSplash, toScreen } from '../engine.js';
import { remote, lineChart3D } from '../props.js';
import { boatScene, boatRig, tagLabel, followPt, FRONT, figureOnStone, pierAt } from './boatkit.js';

const OUTER = 0.15, LOW = -1.6, HIGH = -0.25;

function common(ui, { figure = true, coins = true, chart = false } = {}) {
  const W = boatScene();
  const rig = boatRig(W.scene, {});
  const fg = figure ? figureOnStone(W.scene, { x: -3.5, z: -4.6, ry: 0.45 }) : null;
  let rc = null;
  if (fg) {
    rc = remote();
    rc.scale.setScalar(0.3);
    rc.position.set(0, -0.78, 0.1);
    rc.rotation.x = -0.5;
    fg.fig.userData.armR.add(rc);
  }
  const pier = coins ? pierAt(W.scene, 3.5, -4.4) : null;
  let ch = null;
  if (chart) {
    ch = lineChart3D({ w: 3.2, h: 1.8, series: [{ pts: [[0, 0.05], [0.18, 0.55], [0.4, 0.8], [0.7, 0.92], [1, 0.96]], color: PAL.cinnabar, width: 0.07 }] });
    ch.position.set(-5.6, 1.6, -7.5);
    W.scene.add(ch);
  }
  return { W, rig, fg, rc, pier, ch };
}

function pressRemote(fg, rc, t, t0) {
  const k = easeOut(prog(t, t0 - 0.35, 0.35));
  fg.fig.userData.pose({ armR: lerp(0.3, 1.3, k) - 0.6 * easeIn(prog(t, t0 + 0.25, 0.4)) });
  rc.userData.button.material.emissive = new THREE.Color(PAL.cinnabar);
  rc.userData.button.material.emissiveIntensity = t > t0 && t < t0 + 0.3 ? 1.4 : 0;
}

// ---------------------------------------------------------------- 镜 4：水车
export function pump({ ui }) {
  const { W, rig, fg, rc, pier } = common(ui, { figure: true });
  tagLabel(ui, 'eq', '空调 = 水车', PAL.jade);
  tagLabel(ui, 'coin', '每一斗 = 一份电费', PAL.ochre);
  const tUnfold = cue('pump.ac_unfold'), tStart = cue('pump.pump_start'), tCoin = cue('pump.coin_drop'), tSteady = cue('pump.steady_level');
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: [3.5, 2.2, 21], look: [0.8, -0.6, -2.5], fov: 34 }, { t: 3.6, pos: [4.5, 2.0, 20], look: [1.6, -0.3, -3], fov: 33 },
        { t: 5.2, pos: [2.0, 2.4, 22], look: [0.6, -0.8, -3], fov: 34 }]);
      W.tick(t, OUTER);
      const unfold = easeOut(prog(t, tUnfold, 0.45));
      rig.wheel.scale.set(1, Math.max(0.01, unfold), 1);
      const run = easeInOut(prog(t, tStart, 0.6));
      const pumpPos = Math.max(0, t - tStart) * 1.6 * run;
      rig.set(t, { outer: OUTER, inner: LOW, pump: pumpPos, flow: run });
      rig.boat.userData.ac.userData.set(unfold, '26°', true);
      // 每车出一斗落一枚铜钱：第 8 拍起，每拍一枚
      const n = t < tCoin ? 0 : 1 + Math.floor((t - tCoin) / 0.53) + clamp01(((t - tCoin) % 0.53) / 0.2);
      pier.userData.set(Math.min(n, 8));
      fg.fig.userData.pose({ armR: 0.3 });
      followPt(ui, 'eq', W.camera, [1.0, 2.3, -1.6], easeOut(prog(t, tUnfold + 0.3, 0.4)));
      followPt(ui, 'coin', W.camera, [2.4, 2.9, -4.4], easeOut(prog(t, tCoin + 0.2, 0.4)));
    },
    fx(g, lt, t) {
      const [x, y] = toScreen(rig.boat, W.camera, [2.0, 0.8, -1.6]);
      inkSplash(g, x, y, t - tUnfold, 90, PAL.wood2, 41, 0.5);
    },
  };
}

// ---------------------------------------------------------------- 镜 5：关掉
export function off({ ui }) {
  const { W, rig, fg, rc, pier, ch } = common(ui, { figure: true, chart: true });
  tagLabel(ui, 'store', '船板 = 墙和家具：会存热', PAL.ochre);
  tagLabel(ui, 'chart', '室内温度（示意）', PAL.cinnabar);
  const tStop = cue('off.wheel_stop'), tUp = cue('off.level_up'), tSoak = cue('off.planks_soak'), tShrink = cue('off.jets_shrink'), tDrip = cue('off.last_drip');
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.3, 0.38, 48), new THREE.MeshBasicMaterial({ color: PAL.ink, transparent: true, opacity: 0, side: THREE.DoubleSide }));
  ring.rotation.x = -Math.PI / 2;
  W.scene.add(ring);
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: FRONT.pos, look: FRONT.look, fov: FRONT.fov }, { t: 4.3, pos: [0.4, 1.8, 19], look: [-0.4, -0.9, -2.5], fov: 33 },
        { t: 6.3, pos: [-1.0, 1.6, 17.5], look: [-1.2, -0.8, -2.5], fov: 32 }]);
      W.tick(t, OUTER);
      // 遥控器关机：链条卡死，泥人转身离开
      pressRemote(fg, rc, t, tStop);
      const leave = easeInOut(prog(t, tStop + 0.5, 1.2));
      fg.fig.rotation.y = lerp(0.45, -2.6, leave);
      fg.fig.visible = leave < 0.98;
      const inner = lerp(LOW, HIGH, easeOut(prog(t, tUp, 2.6)) * 0.55 + easeOut(prog(t, tShrink, 2.4)) * 0.45);
      const soak = easeOut(prog(t, tSoak, 2.0));
      rig.set(t, { outer: OUTER, inner, pump: t < tStop ? (t - (tStop - 2)) * 1.6 : 4.0 + 1.6 * 2 + pulse(t, tStop, 9, 30) * 0.05,
        flow: t < tStop ? 1 : clamp01(1 - (t - tStop) / 0.25), soak });
      rig.boat.userData.ac.userData.set(t < tStop ? 1 : 0, t < tStop ? '26°' : '', t < tStop);
      pier.userData.set(8);
      ch.userData.set(0, easeOut(prog(t, tUp, 4.6)));
      // 最后一颗水滴落进船舱水面，荡开墨色圆纹
      const rk = prog(t, tDrip, 0.8);
      ring.position.set(-0.8, inner + 0.03, -1.0);
      ring.scale.setScalar(1 + rk * 3);
      ring.material.opacity = t > tDrip ? 0.7 * (1 - rk) : 0;
      followPt(ui, 'store', W.camera, [-2.3, 1.25, 0], easeOut(prog(t, tSoak + 0.3, 0.4)));
      followPt(ui, 'chart', W.camera, [-4.0, 3.9, -7.5], easeOut(prog(t, tUp + 0.2, 0.4)));
    },
  };
}

// ---------------------------------------------------------------- 镜 6：回来猛车
export function restart({ ui }) {
  const { W, rig, fg, rc, pier } = common(ui, { figure: true });
  tagLabel(ui, 'fast', '转得越快 · 效率越低', PAL.cinnabar);
  const tJolt = cue('restart.restart_jolt'), tSpill = cue('restart.spill_back'), tCoins = cue('restart.coins_rush');
  const sweat = [];
  for (let i = 0; i < 6; i++) {
    const d = new THREE.Mesh(new THREE.SphereGeometry(0.06, 10, 8), new THREE.MeshStandardMaterial({ color: '#BFE6F4', roughness: 0.2 }));
    W.scene.add(d);
    sweat.push(d);
  }
  return {
    scene: W.scene, camera: W.camera,
    update(lt, t) {
      camKeys(W.camera, lt, [{ t: 0, pos: [2.5, -0.6, 17], look: [1.2, 0.2, -2.5], fov: 36 }, { t: 2.1, pos: [-2.2, 0.8, 12], look: [-3.0, 1.4, -4.4], fov: 34 },
        { t: 4.2, pos: [3.0, 1.6, 19], look: [1.6, -0.5, -3.5], fov: 34 }]);
      shake(W.camera, t, tJolt, 0.14);
      W.tick(t, OUTER);
      fg.fig.rotation.y = 0.45;
      pressRemote(fg, rc, t, tJolt);
      const speed = easeOut(prog(t, tJolt, 0.3));
      const pumpPos = Math.max(0, t - tJolt) * 4.5;
      const inner = lerp(HIGH, -0.9, easeInOut(prog(t, tJolt + 0.3, 6.0)));   // 降得慢
      rig.set(t, { outer: OUTER, inner, pump: pumpPos, flow: speed, blur: speed, soak: 1 - 0.6 * prog(t, tJolt, 6), warm: lerp(1, 0.5, prog(t, tJolt, 6)) });
      rig.boat.userData.ac.userData.set(1, '26°', true);
      rig.boat.userData.ac.userData.led.material.emissiveIntensity = 1.4;
      // 铜钱：开头已有 8 枚；第 8 拍起每半拍一枚，更急
      const n = 8 + (t < tCoins ? 0 : (t - tCoins) / 0.26);
      pier.userData.set(Math.min(n, 30));
      // 泥人汗珠飞溅
      fg.fig.updateWorldMatrix(true, true);
      const head = fg.fig.userData.head.getWorldPosition(new THREE.Vector3());
      sweat.forEach((d, i) => {
        const u = ((t * 1.6 + i / sweat.length) % 1);
        d.position.set(head.x + Math.cos(i * 1.7) * (0.3 + u * 0.6), head.y + 0.2 + u * 0.5 - u * u * 1.2, head.z + Math.sin(i * 1.7) * 0.3);
        d.visible = t > tSpill - 0.5;
      });
      fg.fig.userData.pose({ armR: 1.0, nod: 0.08 * Math.sin(t * 12), walk: t * 4, amp: t > tSpill ? 0.6 : 0 });
      followPt(ui, 'fast', W.camera, [1.0, 2.5, -1.6], easeOut(prog(t, tJolt + 0.6, 0.4)));
    },
  };
}
